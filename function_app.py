import azure.functions as func
import json
import logging
import time

app = func.FunctionApp()

# In-memory poll storage (resets when app restarts)
polls = {}

# --- Add sample polls on startup (for local dev/demo) ---
sample_data = [
    {
        "question": "Best Economic Plan?",
        "options": ["Capitalism", "Communism", "Socialism"]
    },
    {
        "question": "Best Season?",
        "options": ["Spring", "Summer", "Autumn", "Winter"]
    },
    {
        "question": "Should Pakistan adopt Secularism?",
        "options": ["YES!", "NO!"]
    }
]
for sample in sample_data:
    poll_id = str(int(time.time() * 1000))
    polls[poll_id] = {
        "poll_id": poll_id,
        "question": sample["question"],
        "options": sample["options"],
        "votes": [0] * len(sample["options"])
    }
    time.sleep(0.01)  # ensure unique poll_id

@app.function_name(name="createPoll")
@app.route(route="createPoll", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def create_poll(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        question = data.get("question")
        options = data.get("options")

        if not question or not options or not isinstance(options, list):
            return func.HttpResponse("Invalid input", status_code=400)

        # Generate a unique poll_id (timestamp string)
        poll_id = str(int(time.time() * 1000))
        poll = {
            "poll_id": poll_id,
            "question": question,
            "options": options,
            "votes": [0] * len(options)
        }
        polls[poll_id] = poll

        return func.HttpResponse(json.dumps(poll), mimetype="application/json", status_code=201)
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
        return func.HttpResponse(json.dumps(polls[poll_id]), mimetype="application/json", status_code=200)
    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error voting in poll", status_code=500)

@app.function_name(name="getPoll")
@app.route(route="getPoll", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_poll(req: func.HttpRequest) -> func.HttpResponse:
    poll_id = req.params.get("poll_id")
    if not poll_id or poll_id not in polls:
        return func.HttpResponse("Poll not found", status_code=404)

    poll = polls[poll_id]
    return func.HttpResponse(json.dumps(poll), mimetype="application/json")

@app.function_name(name="getAllPolls")
@app.route(route="getAllPolls", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_all_polls(req: func.HttpRequest) -> func.HttpResponse:
    # Return all poll objects (not just id/question)
    poll_list = list(polls.values())
    return func.HttpResponse(json.dumps(poll_list), mimetype="application/json")
