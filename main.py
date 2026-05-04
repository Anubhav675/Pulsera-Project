import time
import ntptime
from hardware import Hardware
from display import Display
from menu import EncoderMenu
from sampling import PulseSampler
from processing import HeartRateProcessor
from comms import CommsManager
import config
import storage

# States
MENU, LIVE_HR, HRV_MEASURING, HRV_DONE, HISTORY_VIEW, HISTORY_DETAIL = range(6)


def main():
    
    hw = Hardware()
    display = Display(hw.oled)
    menu = EncoderMenu(hw)
    sampler = PulseSampler()
    processor = HeartRateProcessor()
    net = CommsManager()

    # --- BOOT ---
    display.show_splash()
    time.sleep(3)

    display.show_message("WiFi...")
    net_ok = net.setup()

    if net_ok:
        try:
            ntptime.settime()
        except:
            print("NTP Failed")
        display.show_message("Ready")
    else:
        display.show_message("Offline Mode")

    time.sleep(1)

    # --- START ---
    state = MENU
    locked_index = menu.selected_index()

    history_data = []
    history_index = 0

    display.show_menu(config.MENU_ITEMS, menu.selected_index())
    last_ui_update = 0

    # --- LOOP ---
    while True:
        now = time.ticks_ms()

        
        if state in (LIVE_HR, HRV_MEASURING, HRV_DONE):
            hw.encoder_changed = False
            hw.encoder_index = locked_index

        # ===== MENU =====
        if state == MENU:
            if menu.update():
                display.show_menu(config.MENU_ITEMS, menu.selected_index())

            if menu.was_pressed():
                mode = menu.selected_item()
                locked_index = menu.selected_index()

                # ---- HISTORY ----
                if mode == "History":
                    history_data = storage.load_history()
                    history_index = 0

                    
                    hw.encoder_index = 0

                    state = HISTORY_VIEW

                # ---- KUBIOS ----
                elif mode == "Kubios":
                    if not net._wlan.isconnected():
                        display.show_message("No WiFi!")
                        time.sleep(2)
                        display.show_menu(config.MENU_ITEMS, menu.selected_index())
                        continue

                    processor.reset()
                    sampler.start()
                    measurement_start = now
                    state = HRV_MEASURING

                # ---- BASIC / LIVE ----
                else:
                    processor.reset()
                    sampler.start()
                    measurement_start = now

                    if mode == "Measure HR":
                        state = LIVE_HR
                    else:
                        state = HRV_MEASURING

        # ===== LIVE HR =====
        elif state == LIVE_HR:
            raw = 0

            while sampler.has_sample():
                raw = sampler.get_sample()
                beat, _ = processor.process_sample(raw)
                hw.led.value(1 if beat else 0)

            if time.ticks_diff(now, last_ui_update) > 40:
                display.draw_ppg_wave(processor.average_bpm(), raw)
                last_ui_update = now

            if menu.was_pressed():
                sampler.stop()
                state = MENU
                display.show_menu(config.MENU_ITEMS, menu.selected_index())

        # ===== HRV MEASURING =====
        elif state == HRV_MEASURING:
            raw_val = 0

            while sampler.has_sample():
                raw_val = sampler.get_sample()
                beat, _ = processor.process_sample(raw_val)
                hw.led.value(1 if beat else 0)

            elapsed = time.ticks_diff(now, measurement_start) // 1000
            mode = menu.selected_item()

            if time.ticks_diff(now, last_ui_update) > 1000:
                display.show_collecting(30 - elapsed, mode)
                last_ui_update = now

            if elapsed >= 30 or (menu.was_pressed() and elapsed > 5):
                sampler.stop()

                # ===== KUBIOS =====
                if mode == "Kubios":
                    display.show_message("Analyzing...")

                    try:
                        rris = processor.get_rris()

                        clean_rris = []
                        for x in rris:
                            if 500 <= x <= 1000:
                                clean_rris.append(x)

                        if len(clean_rris) < 10:
                            display.show_message("Bad Data")
                            time.sleep(2)
                            res = None
                        else:
                            res = net.request_analysis(clean_rris)

                    except Exception as e:
                        print("Kubios error:", e)
                        res = None

                    if res and "data" in res and "analysis" in res["data"]:
                        d = res["data"]["analysis"]

                        hr = d.get("mean_hr_bpm", 0)
                        rm = d.get("rmssd_ms", 0)
                        sd = d.get("sdnn_ms", 0)
                        pns = d.get("pns_index", 0)
                        sns = d.get("sns_index", 0)
                        ppi = d.get("mean_rr_ms", 0)

                        display.show_kubios_results(hr, rm, sd, pns, sns)

                        if net._wlan.isconnected():
                            net.save_to_db(hr, rm, sd, pns, sns, ppi)

                        storage.save_result(hr, rm, sd)

                    else:
                        display.show_message("Kubios Error")
                        time.sleep(2)

                # ===== BASIC HRV =====
                else:
                    bpm = processor.average_bpm()
                    rm = processor.rmssd()
                    sd = processor.sdnn()
                    ppi = processor.mean_ppi()

                    storage.save_result(bpm, rm, sd)

                    if net._wlan.isconnected():
                        try:
                            net.save_to_db(bpm, rm, sd)
                        except:
                            print("DB skipped")

                    display.show_hrv_results(bpm, ppi, rm, sd)

                state = HRV_DONE

        # ===== DONE =====
        elif state == HRV_DONE:
            if menu.was_pressed():
                state = MENU
                display.show_menu(config.MENU_ITEMS, menu.selected_index())

        # ===== HISTORY =====
        elif state == HISTORY_VIEW:
            total_options = len(history_data) + 1  # BACK + records

            if menu.update():
                history_index = menu.selected_index() % total_options
                display.show_history_list(history_data, history_index)

            if menu.was_pressed():
                if history_index == 0:
                    state = MENU
                    display.show_menu(config.MENU_ITEMS, menu.selected_index())
                else:
                    sel = history_index - 1
                    display.show_history_detail(
                        history_data[sel], sel, len(history_data)
                    )
                    state = HISTORY_DETAIL

        # ===== HISTORY DETAIL =====
        elif state == HISTORY_DETAIL:
            if menu.was_pressed():
                state = HISTORY_VIEW
                display.show_history_list(history_data, history_index)

        time.sleep_ms(2)


if __name__ == "__main__":
    main()

