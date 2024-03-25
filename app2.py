import replicate
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/bucc-7b-bot/", methods = ["POST", "GET"])
def llama_2_13b():
    if request.method == "POST":
        # Extracting response from JSON
        api_json = request.json

        question = api_json["question"]
        # Specifying AI Info
        context = open("context.txt", "r").read()
       
        # # Extracting response.
        response_list = []
        response_string = ""

        output = replicate.run(
            "meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",
            input={
                "prompt": f"With this info, '{context}'. if a question is 'what is the JAVA course code?', your response should be brief as such 'The JAVA course code is COSC205', follow this short and precise response format. Respond to this without 'of course!' or anything like that, just give the answer to': {question}.",
                "max_new_tokens" : 40,
                "repetition_penalty" : 3,
                "temperature" : 0.8,
            }
        )


        for item in output:
            response_list.append(item)

        response_string = response_string.join(response_list)
        # Clearing response list for next prompt response.
        response_list.clear()

        # return result
        response = {"response" : response_string}
        response_string = "" # Clearing previous response.
        return jsonify(response)
    # Handling Other kinds of requests.
    else:
        info = "This Software Engineering (BUCC) endpoint can only be accessed using a POST request, provide the right inputs as observed below. Previous prompts don't need to be separated with new line characters, just provide them as a continuous string."
        sample_prompt = {
        "question": "What is BUCC?",
        }
        sample_output = {
            "response":"BUCC stands for Babcock University Computer Club and is a popular name for the school of Computing and Engineering Sciences."
        }
        feedback = {
            "Info": info,
            "sample prompt" : sample_prompt,
            "sample output": sample_output
        }
        return jsonify(feedback)


if __name__ == "__main__":
    app.run(debug = False, host = '0.0.0.0', port = 8000)