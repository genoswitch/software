import requests
import random
import string

def getSVG(struc):
    postURL = "https://old.nupack.org/design/update_input_preview"
    postURL2 = "https://old.nupack.org/design/draw_multi_preview"
    input = struc
    token = "".join(random.choice(string.ascii_letters) for i in range(10))
    name = "".join(random.choice(string.ascii_letters) for i in range(10))

    payload = {
        "structure": input,
        "preview_token": token,
        "material": "rna"
    }

    print(payload)

    req = requests.post(postURL, data=payload)

    if req.status_code == 200:

        print("req1 success!")
        tagval = req.text.split("$('multi_tag').value = ")[1].split('"')[1]

        req2 = requests.post(postURL2, data={"tagval": tagval})

        if req2.status_code == 200:

            print("req2 success!!")
            getURL = "https://old.nupack.org/" + req2.text.split("src=")[-1].split("/></td></tr>")[0][1:-12]
            print(getURL)

            req3 = requests.get(getURL)

            if req3.status_code == 200:

                print("req3 success!!!")

                with open(f"struc_{name}.png", "wb") as output:
                    output.write(req3.content)

                # with open("structureSVG.svg", "r") as output:
                #     output = open("structureSVG.svg", "r")
                #     fileLen = len(open("structureSVG.svg", "r").readlines())
                #     lines = open("structureSVG.svg", "r").readlines()
                  
                #     svgKeySpan = list(range(fileLen-78, fileLen-2))
                #     # to remove the label on the side of svg, delete all code from "<g id="axes2">" UP TO AND INCLUDING THE SECOND TO LAST "</g>", 76 lines
        
                # with open("structureSVG.svg", "w") as output:
                #     for i, line in enumerate(lines):
                #         if i not in svgKeySpan:
                #             output.write(line)
    return name

