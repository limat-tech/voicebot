// VOCERY/frontend/src/screens/OrderDetailScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App';

// Type definitions (ensure they are correct)
type OrderItem = {
    product_name: string;
    quantity: number;
    price_at_purchase: number;
};
type OrderDetails = {
    order_id: number;
    order_date: string;
    total_amount: number;
    status: string;
    items: OrderItem[];
};

type OrderDetailScreenProps = StackScreenProps<RootStackParamList, 'OrderDetail'>;

const OrderDetailScreen = ({ route, navigation }: OrderDetailScreenProps) => {
    const { orderId } = route.params;
    const [order, setOrder] = useState<OrderDetails | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrderDetails = async () => {
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) {
                    navigation.replace('Login');
                    return;
                }
                const response = await axios.get(`http://10.0.2.2:5000/api/orders/${orderId}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setOrder(response.data);
            } catch (error) {
                console.error("Failed to fetch order details:", error);
                Alert.alert("Error", "Could not load order details.");
            } finally {
                setLoading(false);
            }
        };
        fetchOrderDetails();
    }, [orderId, navigation]);

    if (loading) {
        return <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />;
    }

    if (!order) {
        return (
            <View style={styles.container}>
                <Text style={styles.emptyText}>Order not found.</Text>
            </View>
        );
    }
    
    const renderOrderItem = ({ item }: { item: OrderItem }) => (
        <View style={styles.itemContainer}>
            <View style={styles.itemDetails}>
                <Text style={styles.itemName}>{item.product_name}</Text>
                <Text style={styles.itemQuantity}>Quantity: {item.quantity}</Text>
            </View>
            <Text style={styles.itemPrice}>AED {item.price_at_purchase.toFixed(2)}</Text>
        </View>
    );

    return (
        <View style={styles.container}>
            {/* --- FIX IS HERE --- */}
            {/* This container is now populated with data, filling the space correctly. */}
            <View style={styles.summaryContainer}>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>Order ID:</Text>
                    <Text style={styles.summaryValue}>#{order.order_id}</Text>
                </View>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>Date:</Text>
                    <Text style={styles.summaryValue}>{new Date(order.order_date).toLocaleDateString()}</Text>
                </View>
                <View style={styles.summaryRow}>
                    <Text style={styles.summaryLabel}>Status:</Text>
                    <Text style={styles.summaryValue}>{order.status}</Text>
                </View>
                <View style={[styles.summaryRow, { marginTop: 10, borderTopWidth: 1, paddingTop: 10, borderColor: '#eee' }]}>
                    <Text style={[styles.summaryLabel, { fontWeight: 'bold' }]}>Total Amount:</Text>
                    <Text style={styles.summaryTotalValue}>AED {order.total_amount.toFixed(2)}</Text>
                </View>
            </View>
            
            <Text style={styles.itemsHeader}>Items in this Order</Text>

            <FlatList
                data={order.items}
                renderItem={renderOrderItem}
                keyExtractor={(item, index) => `${item.product_name}-${index}`}
            />
        </View>
    );
};

// Using the complete styles from your previous request
const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    loader: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    summaryContainer: {
        backgroundColor: '#fff',
        padding: 20,
        marginBottom: 10,
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    summaryRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        paddingVertical: 6,
    },
    summaryLabel: {
        fontSize: 16,
        color: '#666',
    },
    summaryValue: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    summaryTotalValue: {
        fontSize: 18,
        fontWeight: 'bold',
        color: 'green',
    },
    itemsHeader: {
        fontSize: 20,
        fontWeight: 'bold',
        paddingHorizontal: 20,
        paddingTop: 10, // Reduced top padding
        paddingBottom: 10,
    },
    itemContainer: {
        backgroundColor: '#fff',
        paddingHorizontal: 20,
        paddingVertical: 15,
        borderBottomWidth: 1,
        borderBottomColor: '#f0f0f0',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    itemDetails: {
        flex: 1,
    },
    itemName: {
        fontSize: 16,
        fontWeight: '600',
    },
    itemQuantity: {
        fontSize: 14,
        color: '#888',
        marginTop: 4,
    },
    itemPrice: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    emptyText: {
        textAlign: 'center',
        marginTop: 20,
        fontSize: 18,
    }
});

export default OrderDetailScreen;