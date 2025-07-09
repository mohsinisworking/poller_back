import azure.functions as func
import json
import logging

app = func.FunctionApp()

# In-memory poll storage (resets when app restarts)
polls = {}

@app.function_name(name="createPoll")
@app.route(route="createPoll", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def create_poll(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        poll_id = data.get("poll_id")
        question = data.get("question")
        options = data.get("options")

        if not poll_id or not question or not options or not isinstance(options, list):
            return func.HttpResponse("Invalid input", status_code=400)

        if poll_id in polls:
            return func.HttpResponse("Poll ID already exists", status_code=400)

        polls[poll_id] = {
            "question": question,
            "options": options,
            "votes": [0] * len(options)
        }

        return func.HttpResponse(f"Poll '{poll_id}' created.", status_code=201)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error creating poll", status_code=500)

@app.function_name(name="votePoll")
@app.route(route="votePoll", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def vote_poll(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        poll_id = data.get("poll_id")
        option_index = data.get("option_index")

        if poll_id not in polls:
            return func.HttpResponse("Poll not found", status_code=404)

        if not isinstance(option_index, int) or option_index < 0 or option_index >= len(polls[poll_id]["options"]):
            return func.HttpResponse("Invalid option index", status_code=400)

        polls[poll_id]["votes"][option_index] += 1
        return func.HttpResponse("Vote recorded.", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error voting in poll", status_code=500)

@app.function_name(name="getPoll")
@app.route(route="getPoll", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_poll(req: func.HttpRequest) -> func.HttpResponse:
    poll_id = req.params.get("poll_id")
    if not poll_id or poll_id not in polls:
        return func.HttpResponse("Poll not found", status_code=404)

    return func.HttpResponse(json.dumps(polls[poll_id]), mimetype="application/json")

@app.function_name(name="getAllPolls")
@app.route(route="getAllPolls", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_all_polls(req: func.HttpRequest) -> func.HttpResponse:
    poll_list = [
        {"poll_id": poll_id, "question": poll["question"]}
        for poll_id, poll in polls.items()
    ]
    return func.HttpResponse(json.dumps(poll_list), mimetype="application/json")
