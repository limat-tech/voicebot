import React, { useState } from 'react';
import {
    View,
    Text,
    TextInput,
    Button,
    StyleSheet,
    TouchableOpacity,
    Alert,
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App';

type LoginScreenProps = StackScreenProps<RootStackParamList, 'Login'>;

const LoginScreen = ({ navigation }: LoginScreenProps) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async () => {
        if (!email || !password) {
            Alert.alert('Error', 'Email and password are required.');
            return;
        }

        try {
            const response = await axios.post('http://10.0.2.2:5000/api/auth/login', {
                email: email,
                password: password,
            });

            const token = response.data.access_token; // Extract token

            // Store the token in AsyncStorage
            await AsyncStorage.setItem('userToken', token);
            console.log('Token stored successfully.');

            Alert.alert(
                'Success',
                `Logged in!`, // Removed token from alert for security
                [
                    {
                        text: 'OK',
                        onPress: () => navigation.navigate('ProductList'), // Navigate after dismissing alert
                    },
                ]
            );
        } catch (error: any) {
            console.error('Login error:', error.response ? error.response.data : error.message);
            Alert.alert(
                'Login Failed',
                error.response?.data?.error || 'Invalid credentials. Please try again.'
            );
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Login</Text>

            <TextInput
                placeholder="Email"
                style={styles.input}
                keyboardType="email-address"
                autoCapitalize="none"
                value={email}
                onChangeText={setEmail}
            />

            <TextInput
                placeholder="Password"
                style={styles.input}
                secureTextEntry
                value={password}
                onChangeText={setPassword}
            />

            <Button
                title="Login"
                onPress={handleLogin}
            />

            <TouchableOpacity
                style={styles.linkContainer}
                onPress={() => navigation.navigate('Register')}
            >
                <Text style={styles.linkText}>Don't have an account? Register</Text>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        marginBottom: 24,
        textAlign: 'center',
        color: '#333',
    },
    input: {
        height: 45,
        borderColor: '#ddd',
        borderWidth: 1,
        borderRadius: 8,
        marginBottom: 15,
        paddingHorizontal: 15,
        backgroundColor: '#fff',
        fontSize: 16,
    },
    linkContainer: {
        marginTop: 20,
    },
    linkText: {
        color: '#007AFF',
        textAlign: 'center',
        fontSize: 16,
    },
});

export default LoginScreen;
