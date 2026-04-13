import sys
import os
from playwright.sync_api import sync_playwright

def inspect_router():
    url = "http://192.168.18.1"
    output_file = "router_ui_report.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Inspecting Router at {url}...\n")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Go to the URL
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Save screenshot
                page.screenshot(path="router_debug_view.png")
                f.write("Screenshot saved as router_debug_view.png\n")
                
                # Print page title
                f.write(f"Page Title: {page.title()}\n")
                
                # Inspect inputs
                inputs = page.locator("input").all()
                f.write(f"\nFound {len(inputs)} input elements:\n")
                for i, inp in enumerate(inputs):
                    id_attr = inp.get_attribute("id")
                    name_attr = inp.get_attribute("name")
                    type_attr = inp.get_attribute("type")
                    placeholder = inp.get_attribute("placeholder")
                    f.write(f"[{i}] Type: {type_attr}, ID: {id_attr}, Name: {name_attr}, Placeholder: {placeholder}\n")
                    
                # Inspect buttons
                buttons = page.locator("button, input[type='button'], input[type='submit']").all()
                f.write(f"\nFound {len(buttons)} button elements:\n")
                for i, btn in enumerate(buttons):
                    id_attr = btn.get_attribute("id")
                    txt = btn.inner_text().strip() or btn.get_attribute("value")
                    f.write(f"[{i}] ID: {id_attr}, Text/Value: {txt}\n")

                # Also check for frames
                frames = page.frames
                f.write(f"\nFound {len(frames)} frames/iframes.\n")
                for i, frame in enumerate(frames):
                    f.write(f"Frame[{i}] URL: {frame.url}\n")
                    
                # If there are frames, inspect the first one (often the login frame)
                if len(frames) > 1:
                    f.write("\nInspecting first sub-frame:\n")
                    try:
                        frame_inputs = frames[1].locator("input").all()
                        for i, inp in enumerate(frame_inputs):
                            id_attr = inp.get_attribute("id")
                            f.write(f"Frame Input[{i}] ID: {id_attr}\n")
                    except:
                        pass

            except Exception as e:
                f.write(f"Error during inspection: {str(e)}\n")
            finally:
                browser.close()

if __name__ == "__main__":
    inspect_router()
