import streamlit as st
import requests

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Personal Assistant",
    page_icon="🤝"
)

# -----------------------------
# TITLE
# -----------------------------
st.title("🤝 Your Personal Assistant")

st.subheader("What can your personal assistant do?")

st.markdown("""
1. Answer questions on various topics.
2. Arrange Calendar events and meetings.
3. Read your emails and send replies, and summarize them.
4. Manage your tasks and to-do lists.
5. Take quick notes for you.
6. Track your expenses and budgeting.
""")

st.subheader("💬 Chat with your assistant")

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# CHAT INPUT
# -----------------------------
user_message = st.chat_input("Your message")

# -----------------------------
# HANDLE USER MESSAGE
# -----------------------------
if user_message:

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_message)

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # -----------------------------
    # SEND MESSAGE TO N8N
    # -----------------------------
    try:

        with st.spinner("Assistant is thinking..."):

            # response = requests.post(
            #     "http://localhost:5678/webhook-test/c3d9ce33-22f0-46f9-a658-c8dfac8bc7e1",
            #     json={
            #         "query": user_message
            #     },
            #     timeout=120
            # )
            # response = requests.post(
            #      "http://localhost:5678/webhook-test/c3d9ce33-22f0-46f9-a658-c8dfac8bc7e1",
            #      json={"query": user_message},
            #      timeout=120  
# )
            response = requests.post(
                    "http://localhost:5678/webhook/c3d9ce33-22f0-46f9-a658-c8dfac8bc7e1",
                    json={"chatInput": user_message},

                    timeout=120
)
        # Debug information in terminal
        print("STATUS CODE:", response.status_code)
        print("CONTENT TYPE:", response.headers.get("content-type"))
        print("RAW RESPONSE:", repr(response.text))

        # Check HTTP error
        response.raise_for_status()

        # -----------------------------
        # HANDLE N8N RESPONSE
        # -----------------------------
        if not response.text.strip():

            ai_response = (
                "⚠️ n8n returned an empty response. "
                "Check your Webhook response settings."
            )

        else:

            try:
                data = response.json()

                print("JSON RESPONSE:", data)
                print("RESPONSE TYPE:", type(data))

                # Response is LIST
                if isinstance(data, list):

                    if len(data) > 0:

                        first_item = data[0]

                        if isinstance(first_item, dict):
                            ai_response = (
                                first_item.get("output")
                                or first_item.get("response")
                                or first_item.get("text")
                                or first_item.get("message")
                                or str(first_item)
                            )
                        else:
                            ai_response = str(first_item)

                    else:
                        ai_response = "⚠️ n8n returned an empty list."

                # Response is DICTIONARY
                elif isinstance(data, dict):

                    ai_response = (
                        data.get("output")
                        or data.get("response")
                        or data.get("text")
                        or data.get("message")
                        or str(data)
                    )

                # Any other JSON response
                else:
                    ai_response = str(data)

            # n8n returned plain text instead of JSON
            except ValueError:

                ai_response = response.text

        # -----------------------------
        # DISPLAY AI RESPONSE
        # -----------------------------
        with st.chat_message("assistant"):
            st.markdown(ai_response)

        # Save AI response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": ai_response
            }
        )

    # -----------------------------
    # CONNECTION ERROR
    # -----------------------------
    except requests.exceptions.ConnectionError:

        error_message = (
            "❌ Cannot connect to n8n. "
            "Make sure n8n is running on localhost:5678."
        )

        with st.chat_message("assistant"):
            st.error(error_message)

    # -----------------------------
    # TIMEOUT ERROR
    # -----------------------------
    except requests.exceptions.Timeout:

        error_message = (
            "⏳ n8n took too long to respond. "
            "Please try again."
        )

        with st.chat_message("assistant"):
            st.error(error_message)

    # -----------------------------
    # OTHER REQUEST ERROR
    # -----------------------------
    except requests.exceptions.RequestException as error:

        error_message = f"❌ n8n request error: {error}"

        with st.chat_message("assistant"):
            st.error(error_message)

    # -----------------------------
    # UNKNOWN ERROR
    # -----------------------------
    except Exception as error:

        error_message = f"❌ Unexpected error: {error}"

        with st.chat_message("assistant"):
            st.error(error_message)