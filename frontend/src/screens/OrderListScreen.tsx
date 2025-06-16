// VOCERY/frontend/src/screens/OrderListScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App'; // Adjust path if needed

// --- FIX IS HERE: Step 1 ---
// Define a specific type for the order summary data
type OrderSummary = {
    order_id: number;
    order_date: string;
    total_amount: number;
    status: string;
};

// Define the props type for this screen using StackScreenProps
type OrderListScreenProps = StackScreenProps<RootStackParamList, 'OrderList'>;

const OrderListScreen = ({ navigation }: OrderListScreenProps) => {
    // Tell TypeScript that the state will hold an array of OrderSummary objects
    const [orders, setOrders] = useState<OrderSummary[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) {
                    navigation.replace('Login');
                    return;
                }
                const response = await axios.get('http://10.0.2.2:5000/api/orders/', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setOrders(response.data);
            } catch (error) {
                console.error("Failed to fetch orders:", error);
                Alert.alert("Error", "Could not load your orders.");
            } finally {
                setLoading(false);
            }
        };
        fetchOrders();
    }, [navigation]);

    // --- FIX IS HERE: Step 2 ---
    // Explicitly type the 'item' in the renderItem function
    const renderItem = ({ item }: { item: OrderSummary }) => (
        <TouchableOpacity style={styles.itemContainer} onPress={() => navigation.navigate('OrderDetail', { orderId: item.order_id })}>
            <Text style={styles.orderId}>Order #{item.order_id}</Text>
            <Text style={styles.orderDate}>Placed on: {new Date(item.order_date).toLocaleDateString()}</Text>
            <View style={styles.orderInfoRow}>
                <Text style={styles.orderStatus}>Status: {item.status}</Text>
                <Text style={styles.orderTotal}>${item.total_amount.toFixed(2)}</Text>
            </View>
        </TouchableOpacity>
    );

    if (loading) return <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />;
    
    return (
        <FlatList
            style={styles.container}
            data={orders}
            renderItem={renderItem}
            keyExtractor={(item) => item.order_id.toString()}
            ListEmptyComponent={<View style={styles.emptyContainer}><Text style={styles.emptyText}>You have no past orders.</Text></View>}
        />
    );
};

const styles = StyleSheet.create({container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    loader: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    // The main "card" for each order in the list
    itemContainer: {
        backgroundColor: '#fff',
        padding: 15,
        marginVertical: 8,
        marginHorizontal: 10,
        borderRadius: 10,
        elevation: 3, // Shadow for Android
        shadowColor: '#000', // Shadow for iOS
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.2,
        shadowRadius: 1.41,
    },
    orderId: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 5,
    },
    orderDate: {
        fontSize: 14,
        color: '#888',
        marginBottom: 10,
    },
    orderInfoRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: 10,
        borderTopWidth: 1,
        borderTopColor: '#eee',
        paddingTop: 10,
    },
    orderStatus: {
        fontSize: 15,
        fontWeight: '500',
        fontStyle: 'italic',
        color: '#555',
    },
    orderTotal: {
        fontSize: 16,
        fontWeight: 'bold',
        color: 'green',
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 50,
    },
    emptyText: {
        fontSize: 18,
        color: '#888',
    },
});
export default OrderListScreen;