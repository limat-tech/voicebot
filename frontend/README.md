# Voice-Assisted Grocery App - Frontend (React Native)

This folder contains the React Native mobile application.

## How to Run

1.  Navigate to this directory: `cd frontend`
2.  Install dependencies: `npm install`
3.  Ensure the Flask backend is running.
4.  Run the app on Android: `npx react-native run-android`

## Core Libraries Used

*   **Navigation**: `react-navigation`
*   **API Calls**: `axios`
*   **Local Storage**: `@react-native-async-storage/async-storage`

## Screens

*   **LoginScreen.tsx**: Handles user login.
*   **RegisterScreen.tsx**: Handles new user registration.
*   **ProductListScreen.tsx**: Displays all products and includes search functionality.
*   **ProductDetailScreen.tsx**: Shows details for a single product.
*   **CartScreen.tsx**: Displays items in the user's cart.
*   **ProfileScreen.tsx**: Shows user info and contains the logout button.
