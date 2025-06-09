// VOCERY/frontend/src/screens/ProfileScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { CommonActions } from '@react-navigation/native'; // <-- IMPORT THIS

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App';

// Type definitions...
type UserProfile = {
    name: string;
    email: string;
    phone_number?: string;
};
type ProfileScreenProps = StackScreenProps<RootStackParamList, 'Profile'>;

const ProfileScreen = ({ navigation }: ProfileScreenProps) => {
    const [user, setUser] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchProfile = async () => {
            // ... (your existing fetchProfile logic remains the same)
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) {
                    navigation.dispatch(CommonActions.reset({ index: 0, routes: [{ name: 'Login' }] }));
                    return;
                }
                const response = await axios.get('http://10.0.2.2:5000/api/auth/profile', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setUser(response.data);
            } catch (error: any) {
                if (error.response?.status === 401) {
                    Alert.alert("Session Expired", "Please log in again.");
                    await AsyncStorage.removeItem('userToken');
                    navigation.dispatch(CommonActions.reset({ index: 0, routes: [{ name: 'Login' }] }));
                } else {
                    Alert.alert("Error", "Could not load profile information.");
                }
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [navigation]);

    // --- FIX IS HERE ---
    const handleLogout = async () => {
        try {
            // Remove the token from storage
            await AsyncStorage.removeItem('userToken');

            // Dispatch the reset action to wipe the navigation history
            navigation.dispatch(
                CommonActions.reset({
                    index: 0, // The index of the active screen in the new stack
                    routes: [
                        { name: 'Login' }, // The new navigation stack only contains the Login screen
                    ],
                })
            );
        } catch (error) {
            console.error("Failed to logout:", error);
            Alert.alert("Error", "Could not log out. Please try again.");
        }
    };

    if (loading) {
        return <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />;
    }

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Your Profile</Text>
            {user ? (
                <View style={styles.infoBox}>
                    <View style={styles.infoRow}>
                        <Text style={styles.label}>Name:</Text>
                        <Text style={styles.value}>{user.name}</Text>
                    </View>
                    <View style={styles.infoRow}>
                        <Text style={styles.label}>Email:</Text>
                        <Text style={styles.value}>{user.email}</Text>
                    </View>
                    {user.phone_number && (
                        <View style={styles.infoRow}>
                            <Text style={styles.label}>Phone:</Text>
                            <Text style={styles.value}>{user.phone_number}</Text>
                        </View>
                    )}
                </View>
            ) : (
                <Text>Could not load profile information.</Text>
            )}
            {/* Added your previously added "My Orders" button */}
            <View style={styles.buttonContainer}>
                <Button title="My Orders" onPress={() => navigation.navigate('OrderList')} />
            </View>
            <View style={styles.buttonContainer}>
                <Button title="Logout" onPress={handleLogout} color="#ff3b30" />
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, padding: 20, backgroundColor: '#f5f5f5' },
    loader: { flex: 1, justifyContent: 'center', alignItems: 'center' },
    title: { fontSize: 28, fontWeight: 'bold', marginBottom: 20 },
    infoBox: { backgroundColor: '#fff', padding: 20, borderRadius: 10 },
    infoRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: '#eee' },
    label: { fontSize: 16, color: '#666' },
    value: { fontSize: 16, fontWeight: '600' },
    buttonContainer: { marginTop: 20 }
});

export default ProfileScreen;