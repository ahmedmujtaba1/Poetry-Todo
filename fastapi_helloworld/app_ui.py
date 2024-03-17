import streamlit as st
import requests

# BACKEND_URL = "https://400c-119-155-209-109.ngrok-free.app"
BACKEND_URL = "http://127.0.0.1:8000"

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
            st.session_state['auth_token'] = token  # Save the auth token in the session state
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
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose the app mode",
                                    ["Home", "Login", "SignUp"])

    if app_mode == "Home":
        show_home_page()
    elif app_mode == "Login":
        show_login_page()
    elif app_mode == "SignUp":
        show_signup_page()
    elif app_mode == "To-Do":
        if 'auth_token' in st.session_state:
            show_todo_page(st.session_state['auth_token'])
        else:
            st.warning("Please login to view this page.")

if __name__ == '__main__':
    st.set_page_config(page_title='To-Do App', layout='wide')
    main()
