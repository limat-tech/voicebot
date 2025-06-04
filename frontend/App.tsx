import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import ProductListScreen from './src/screens/ProductListScreen';


export type RootStackParamList = {
  Login: undefined; // Login screen takes no parameters
  Register: undefined; // Register screen takes no parameters
  ProductList: undefined; // ProductList screen takes no parameters (for now)
  // Add other screens and their params here later
  // Example: ProductDetail: { productId: string };
};

const Stack = createStackNavigator<RootStackParamList>();

const App = () => {
  return (
    <NavigationContainer>
      {/* NavigationContainer is the root component that manages navigation state */}
      <Stack.Navigator
        initialRouteName="Login" // The first screen to show when the app loads
        screenOptions={{ // Default options for all screens in this navigator
          headerStyle: {
            backgroundColor: '#007AFF', // A blue header background
          },
          headerTintColor: '#fff', // White text color for the header title
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {/* Define each screen in the stack */}
        <Stack.Screen
          name="Login" // This name is used to navigate to this screen (e.g., navigation.navigate('Login'))
          component={LoginScreen}
          options={{ title: 'Welcome Back!' }} // Sets the header title for this screen
        />
        <Stack.Screen
          name="Register"
          component={RegisterScreen}
          options={{ title: 'Create Your Account' }}
        />
        {<Stack.Screen
          name="ProductList"
          component={ProductListScreen}
          options={{ title: 'Products' }}
        />}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
