// VOCERY/frontend/App.tsx

import 'react-native-gesture-handler';
import React, { useEffect, useState } from 'react'; // Assuming you still have the login check logic
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import your screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import ProductListScreen from './src/screens/ProductListScreen';
import ProductDetailScreen from './src/screens/ProductDetailScreen'; // <-- IMPORT THE NEW SCREEN
import ProfileScreen from './src/screens/ProfileScreen';
import CartScreen from './src/screens/CartScreen';
import OrderListScreen from './src/screens/OrderListScreen';
import OrderDetailScreen from './src/screens/OrderDetailScreen';


// Define the type for all screens and their parameters
export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  ProductList: undefined;
  ProductDetail: { productId: number }; // <-- MAKE SURE THIS IS ADDED
  Profile: undefined;
  Cart: undefined;
  OrderList: undefined;
  OrderDetail: { orderId: number };
};

const Stack = createStackNavigator<RootStackParamList>();

const App = () => {
    // This logic checks for a token on app start to handle persistent login
    // Keeping it from the previous step.
    const [initialRoute, setInitialRoute] = useState<'Login' | 'ProductList' | null>(null); 

    useEffect(() => {
        const bootstrapApp = async () => {
            try {
                const token = await AsyncStorage.getItem('userToken');
                // If a token exists, set the initial route to the product list.
                // Otherwise, set it to the login screen.
                setInitialRoute(token ? 'ProductList' : 'Login');
            } catch (error) {
                console.error('Error bootstrapping app:', error);
                // Default to Login screen on any error
                setInitialRoute('Login');
            }
        };

        bootstrapApp();
    }, []);

    // Show a loading screen or null while checking the token to avoid a flicker
    if (!initialRoute) {
        return null; // Or a loading spinner component
    }

    return (
        <NavigationContainer>
            <Stack.Navigator
                initialRouteName={initialRoute} // Dynamically set the initial route
                screenOptions={{
                    headerStyle: { backgroundColor: '#f8f8f8' },
                    headerTintColor: '#007AFF',
                    headerTitleStyle: { fontWeight: 'bold' },
                }}
            >
                {/* Define each screen in the stack */}
                <Stack.Screen
                    name="Login"
                    component={LoginScreen}
                    options={{ title: 'Welcome Back!' }}
                />
                <Stack.Screen
                    name="Register"
                    component={RegisterScreen}
                    options={{ title: 'Create Your Account' }}
                />
                <Stack.Screen
                    name="ProductList"
                    component={ProductListScreen}
                    options={{ title: 'Products' }}
                />
                {/* REGISTER THE NEW SCREEN */}
                <Stack.Screen
                    name="ProductDetail"
                    component={ProductDetailScreen}
                    options={{ title: 'Product Details' }}
                />
                <Stack.Screen
                    name="Profile"
                    component={ProfileScreen}
                    options={{ title: 'Your Profile' }}
                />
                <Stack.Screen 
                    name="Cart" 
                    component={CartScreen} 
                    options={{ title: 'Your Cart' }}
                />
                <Stack.Screen 
                name="OrderList" 
                component={OrderListScreen} 
                options={{ title: 'My Orders' }} 
                />
                <Stack.Screen 
                name="OrderDetail" 
                component={OrderDetailScreen} 
                options={{ title: 'Order Details' }} 
                />
            </Stack.Navigator>
        </NavigationContainer>
    );
};

export default App;
