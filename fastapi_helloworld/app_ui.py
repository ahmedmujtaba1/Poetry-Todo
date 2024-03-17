import streamlit as st
import requests

# BACKEND_URL = "https://400c-119-155-209-109.ngrok-free.app"
BACKEND_URL = "http://127.0.0.1:8000"

def clear_token():
    if 'auth_token' in st.session_state:
        del st.session_state['auth_token']
    st.experimental_set_query_params(auth_token=None)

def check_for_token():
    query_params = st.experimental_get_query_params()
    if 'auth_token' in query_params:
        return query_params['auth_token'][0]
    return None

def save_token(token):
    st.session_state['auth_token'] = token
    st.experimental_set_query_params(auth_token=token)

def show_logout_button():
    if st.sidebar.button('Logout'):
        clear_token()
        st.sidebar.success("You've been logged out.")
        st.experimental_rerun()

def show_home_page():
    st.title("To-Do App")
    st.info("Use the sidebar to navigate between Login and SignUp")

def show_login_page():
    st.subheader("Login Section")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    
    if st.sidebar.button("Login"):
        response = requests.post(f"{BACKEND_URL}/token", data={"username": username, "password": password})
        if response.status_code == 200:
            st.sidebar.success("Logged In as {}".format(username))
            token = response.json().get("access_token")
            save_token(token)
            show_todo_page(token)
        else:
            st.sidebar.error("Incorrect Username/Password")

def show_signup_page():
    st.subheader("Create New Account")
    new_user = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type='password')
    
    if st.sidebar.button("Create Account"):
        response = requests.post(f"{BACKEND_URL}/users/", json={"username": new_user, "password": new_password})
        if response.status_code == 200:
            st.sidebar.success("You have successfully created a new account!")
            show_login_page()
        else:
            st.sidebar.error("Username already taken")


def show_todo_page(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    with st.form(key='todo_form'):
        title = st.text_input("Title")
        description = st.text_area("Description")
        submit_button = st.form_submit_button(label='Add To-Do')
        
    if submit_button:
        todo_data = {"title": title, "description": description}
        response = requests.post(f"{BACKEND_URL}/todos/", json=todo_data, headers=headers)
        if response.status_code in [200, 201]:
            st.success("To-Do added successfully!")
            st.experimental_rerun()
        else:
            st.error("Failed to add To-Do.")
    
    display_todos(token, headers)

def display_todos(token, headers):
    todos_response = requests.get(f"{BACKEND_URL}/todos/", headers=headers)
    if todos_response.status_code == 200:
        todos = todos_response.json()
        for todo in todos:
            with st.expander(f"{todo['title']}"):
                st.write(f"Description: {todo['description']}")
                st.write(f"Completed: {'Yes' if todo['completed'] else 'No'}")
                
                if st.button("Mark as completed", key=f"complete_{todo['id']}"):
                    requests.put(f"{BACKEND_URL}/todos/{todo['id']}", json={"completed": True}, headers=headers)
                    st.experimental_rerun()
                
                if st.button("Delete", key=f"delete_{todo['id']}"):
                    requests.delete(f"{BACKEND_URL}/todos/{todo['id']}", headers=headers)
                    st.experimental_rerun()


def main():
    # Check if the user is already authenticated by looking for a token
    token = check_for_token()

    st.sidebar.title("Navigation")
    if token:
        app_mode = st.sidebar.selectbox("Choose the app mode",
                                        ["Home", "To-Do", "Logout"])
    else:
        app_mode = st.sidebar.selectbox("Choose the app mode",
                                        ["Home", "Login", "SignUp"])

    if app_mode == "Home":
        show_home_page()
    elif app_mode == "Login":
        show_login_page()
    elif app_mode == "SignUp":
        show_signup_page()
    elif app_mode == "To-Do" and token:
        show_todo_page(token)
    elif app_mode == "Logout":
        clear_token()
        show_home_page()
    else:
        st.warning("Please login to view this page.")

    if token:
        show_logout_button()

if __name__ == '__main__':
    st.set_page_config(page_title='To-Do App', layout='wide')
    main()
