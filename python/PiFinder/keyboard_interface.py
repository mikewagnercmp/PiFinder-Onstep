from time import sleep


class KeyboardInterface:
    NA = 10
    UP = 11
    DN = 12
    ENT = 13
    A = 20
    B = 21
    C = 22
    D = 24
    ALT_UP = 101
    ALT_DN = 102
    ALT_A = 103
    ALT_B = 104
    ALT_C = 105
    ALT_D = 106
    ALT_0 = 110
    LNG_A = 200
    LNG_B = 201
    LNG_C = 202
    LNG_D = 203
    LNG_ENT = 204

    def run_keyboard(self, q, script_path=None):
        pass

    def run_script(self, q, script_path):
        """
        Runs a keyscript for automation/testing
        """
        print("Running Script: " + script_path)
        with open(script_path + ".pfs", "r") as script_file:
            for script_line in script_file:
                sleep(0.5)
                script_line = script_line.strip()
                print(f"\t{script_line}")
                script_tokens = script_line.split(" ")
                if script_tokens[0].startswith("#"):
                    # comment
                    pass
                elif script_tokens[0] == "":
                    # blank line
                    pass
                elif script_tokens[0] == "wait":
                    sleep(int(script_tokens[1]))
                else:
                    # must be keycode
                    if script_tokens[0].isnumeric():
                        q.put(int(script_tokens[0]))
                    else:
                        q.put(eval(script_tokens[0]))

    def set_brightness(self, level, cfg):
        pass
