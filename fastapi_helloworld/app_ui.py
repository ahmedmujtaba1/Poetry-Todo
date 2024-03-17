import streamlit as st
import requests

# BACKEND_URL = "https://400c-119-155-209-109.ngrok-free.app"
BACKEND_URL = "http://127.0.0.1:8000"

def main():
    st.title("To-Do App")

    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")

    elif choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            response = requests.post(f"{BACKEND_URL}/token", data={"username": username, "password": password})
            if response.status_code == 200:
                st.success("Logged In as {}".format(username))
                token = response.json().get("access_token")
                todos_response = requests.get(f"{BACKEND_URL}/todos/", headers={"Authorization": f"Bearer {token}"})
                if todos_response.status_code == 200:
                    todos = todos_response.json()
                    for todo in todos:
                        st.write(todo)
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("SignUp"):
            response = requests.post(f"{BACKEND_URL}/users/", json={"username": new_user, "password": new_password})
            if response.status_code == 200:
                st.success("You have successfully created a new account!")
                st.info("Go to the Login Menu to login")
            else:
                st.error("Username already taken")

if __name__ == '__main__':
    main()
