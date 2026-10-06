# Delivery Company Agent

An AI operations assistant for a delivery company, built with [Pydantic AI](https://ai.pydantic.dev/). Managers and staff chat with it in Arabic to look up shipments, analyze operations, and perform shipment actions through a shipping API, instead of clicking through dashboards.

The agent works against [`shipping-api-mock`](https://github.com/Abdullah-Mahmoud-Ai/shipping-api-mock), a companion mock API, so the whole project runs locally without a real backend.

## Features

- **Arabic chat interface** built with Streamlit
- **Structured answers**: a clear summary, key metrics, operational insights, proposed actions, and draft messages
- **15 tools** for analytics and shipment operations (see below)
- **Built-in safety rules** for risky actions such as cancellations

### Analytics and lookup tools

| Tool | What it does |
| --- | --- |
| `get_management_overview` | Company summary: shipments, deliveries, delays, returns, cancellations, collected and pending revenue |
| `get_shipments` | Lists shipments, optionally filtered by status and branch |
| `get_shipment_by_id` | Details of a single shipment |
| `get_delayed_shipments` | All delayed shipments |
| `get_returned_shipments` | Shipments that were returned |
| `get_returns` | Return records with reasons and refund values |
| `get_payment_summary` | Paid, pending, and refunded amounts |
| `get_branches_performance` | Per-branch indicators: totals, delivered, delayed, returned, cancelled, collected revenue |
| `get_executive_report_data` | Combines the data above for an executive report |

### Action tools

| Tool | What it does |
| --- | --- |
| `create_shipment` | Creates a shipment (customer, branch, route, expected delivery, amount, weight) |
| `update_shipment` | Edits customer name, destination city, expected delivery, amount, or weight |
| `change_shipment_status` | Sets the status to `delivered`, `in_transit`, `delayed`, `returned`, or `cancelled` |
| `reschedule_shipment` | Changes the expected delivery date |
| `cancel_shipment` | Soft-cancels a shipment, a reason is required |
| `draft_follow_up_message` | Drafts a follow-up message for a branch or an internal team, it never sends it |

## Safety by design

- **Cancellation needs a reason.** If the user does not give one, the agent asks for it instead of inventing one, and the tool refuses to run with an empty reason (`CANCELLATION_REASON_REQUIRED!`).
- **Soft cancellation only.** Cancelled shipments stay in the system. If a user asks to permanently delete a shipment, the agent explains this.
- **Drafts are never sent.** Follow-up messages are marked `requires_human_approval` and are left for a person to review.
- **No invented data.** The agent is instructed not to make up shipment numbers or statuses, to rely only on tool and API data, and to ask for clarification when a request is ambiguous.
- **Readable API errors.** Failures from the shipping API are caught and returned to the agent as `API_ERROR` messages instead of crashing the chat.

## Architecture

```
Streamlit UI (app.py)
        |
        v
Pydantic AI agent (agent.py)  -->  structured output: OperationAnswer
        |  tool calls
        v
ShippingAPIClient (api_client.py)
        |  HTTP
        v
Shipping API (shipping-api-mock)
```

1. The user writes a request in Arabic.
2. The agent picks the right tool and fills in its arguments.
3. The tool calls the shipping API through `ShippingAPIClient`.
4. The agent returns a structured answer (`OperationAnswer`) that the UI displays.

## Example prompts

| Prompt (Arabic) | Meaning |
| --- | --- |
| `قم بإلغاء الشحنة SHP-1020 لأن العميل رفض الاستلام` | Cancel shipment SHP-1020 because the customer refused delivery |
| `ما الشحنات المتأخرة؟` | Which shipments are delayed? |
| `أعطني ملخصًا إداريًا عن الشركة` | Give me an executive summary of the company |
| `ما أفضل الفروع أداءً؟` | Which branches perform best? |

## Project structure

```
delivery-company-agent/
├── agent.py        # Pydantic AI agent: instructions, tools, dependencies
├── api_client.py   # ShippingAPIClient and ShippingAPIError
├── models.py       # Data models, including the OperationAnswer output
├── app.py          # Streamlit chat UI (Arabic)
├── web_chat.py     # Development-only chat UI (Pydantic AI web UI) for testing the tools
├── test_agent.py   # Agent tests
├── test_client.py  # API client tests
├── src/            # Default uv package scaffold (placeholder, not used by the app)
├── pyproject.toml  # Dependencies and project settings
├── uv.lock         # Locked dependency versions
└── .python-version # Pinned Python version
```

## Getting started

### Requirements

- [uv](https://docs.astral.sh/uv/) (it uses the Python version pinned in `.python-version`)
- An OpenAI API key (the agent uses `openai:gpt-5.4-mini`, you can change the model in `agent.py`)

### Installation

```bash
git clone https://github.com/Abdullah-Mahmoud-Ai/delivery-company-agent.git
cd delivery-company-agent
uv sync
```

### Configuration

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here

# Optional, the defaults are shown
SHIPPING_API_BASE_URL=http://127.0.0.1:8000
SHIPPING_API_KEY=demo-shipping-key
```

| Variable | Description | Default |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI key used by the agent | required |
| `SHIPPING_API_BASE_URL` | Base URL of the shipping API | `http://127.0.0.1:8000` |
| `SHIPPING_API_KEY` | API key sent to the shipping API | `demo-shipping-key` |

> The `.env` file is listed in `.gitignore`. Never commit it or share your API key.

### Run

1. Start the mock shipping API (see the [`shipping-api-mock`](https://github.com/Abdullah-Mahmoud-Ai/shipping-api-mock) README):

```bash
uv run uvicorn main:app --reload
```

2. In a second terminal, start the chat app from this project's folder:

```bash
uv run streamlit run app.py
```

## Tech stack

- Python
- [Pydantic AI](https://ai.pydantic.dev/)
- [Streamlit](https://streamlit.io/)
- [uv](https://docs.astral.sh/uv/)
