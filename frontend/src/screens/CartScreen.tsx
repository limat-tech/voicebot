// VOCERY/frontend/src/screens/CartScreen.tsx
import React, { useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, Alert, Button, TouchableOpacity } from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App';

// Updated CartItem type to include Arabic name
type CartItem = {
    cart_item_id: number;
    product_id: number;
    name_en: string;
    name_ar: string;          // Added Arabic name field
    price_per_unit: number;
    quantity: number;
    subtotal: number;
    image_url?: string;
    unit_type?: string;
};

type CartScreenProps = StackScreenProps<RootStackParamList, 'Cart'>;

const CartScreen = ({ navigation }: CartScreenProps) => {
    const [items, setItems] = useState<CartItem[]>([]);
    const [totalPrice, setTotalPrice] = useState<number>(0);
    const [loading, setLoading] = useState<boolean>(true);

    const fetchCartData = async () => {
        setLoading(true);
        try {
            const token = await AsyncStorage.getItem('userToken');
            if (!token) {
                navigation.replace('Login');
                return;
            }
            const response = await axios.get('http://10.0.2.2:5000/api/cart', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setItems(response.data.items || []);
            setTotalPrice(response.data.total_price || 0);
        } catch (error) {
            console.error("Failed to fetch cart:", error);
            Alert.alert("Error", "Could not load your cart.");
        } finally {
            setLoading(false);
        }
    };

    useFocusEffect(useCallback(() => { fetchCartData(); }, []));

    const handleUpdateQuantity = async (itemId: number, newQuantity: number) => {
        try {
            const token = await AsyncStorage.getItem('userToken');
            await axios.patch(`http://10.0.2.2:5000/api/cart/items/${itemId}`, 
                { quantity: newQuantity },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            // Refresh the cart data to show updated totals and quantities
            await fetchCartData();
        } catch (error: any) {
            Alert.alert("Error", `Could not update quantity. ${error.response?.data?.error || ''}`);
        }
    };

    const handleRemoveItem = async (cartItemId: number) => {
        try {
            const token = await AsyncStorage.getItem('userToken');
            await axios.delete(`http://10.0.2.2:5000/api/cart/items/${cartItemId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            Alert.alert("Success", "Item removed from cart.");
            await fetchCartData(); // Refresh cart data
        } catch (error: any) {
            console.error("Failed to remove item:", error);
            Alert.alert("Error", `Could not remove item. ${error.response?.data?.error || ''}`);
        }
    };
    
    const handleCheckout = async () => {
        try {
            const token = await AsyncStorage.getItem('userToken');
            const response = await axios.post('http://10.0.2.2:5000/api/cart/checkout', {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            Alert.alert(
                "Order Placed!",
                `Your order #${response.data.order_id} has been placed successfully.`,
                [{ text: "OK", onPress: () => navigation.navigate('ProductList') }]
            );
        } catch (error: any) {
            console.error("Checkout failed:", error);
            Alert.alert("Checkout Failed", `${error.response?.data?.error || 'Please try again.'}`);
        }
    };

    // Updated renderItem with bilingual support
    const renderItem = ({ item }: { item: CartItem }) => (
        <View style={styles.itemContainer}>
            {/* Bilingual Product Names - English as primary, Arabic as secondary */}
            <View style={styles.nameContainer}>
                <Text style={styles.itemNamePrimary}>{item.name_en}</Text>
                {item.name_ar && (
                    <Text style={styles.itemNameSecondary}>{item.name_ar}</Text>
                )}
            </View>
            
            <View style={styles.itemDetailsRow}>
                {/* Quantity Stepper */}
                <View style={styles.quantityContainer}>
                    <TouchableOpacity 
                        style={styles.quantityButton} 
                        onPress={() => handleUpdateQuantity(item.cart_item_id, item.quantity - 1)}
                    >
                        <Text style={styles.quantityButtonText}>-</Text>
                    </TouchableOpacity>
                    <Text style={styles.quantityText}>{item.quantity}</Text>
                    <TouchableOpacity 
                        style={styles.quantityButton} 
                        onPress={() => handleUpdateQuantity(item.cart_item_id, item.quantity + 1)}
                    >
                        <Text style={styles.quantityButtonText}>+</Text>
                    </TouchableOpacity>
                </View>
                <Text style={styles.itemPrice}>${item.subtotal.toFixed(2)}</Text>
            </View>
            
            <TouchableOpacity 
                onPress={() => handleRemoveItem(item.cart_item_id)} 
                style={styles.removeButton}
            >
                <Text style={styles.removeButtonText}>Remove</Text>
            </TouchableOpacity>
        </View>
    );

    if (loading) {
        return <ActivityIndicator size="large" color="#007AFF" style={styles.loader} />;
    }

    return (
        <View style={styles.container}>
            <FlatList
                data={items}
                renderItem={renderItem}
                keyExtractor={(item) => item.cart_item_id.toString()}
                ListEmptyComponent={<Text style={styles.emptyText}>Your cart is empty.</Text>}
                ListFooterComponent={
                    items.length > 0 ? (
                        <View style={styles.footer}>
                            <Text style={styles.totalText}>Total: ${totalPrice.toFixed(2)}</Text>
                            <Button title="Proceed to Checkout" onPress={handleCheckout} />
                        </View>
                    ) : null
                }
            />
        </View>
    );
};

// Updated styles with bilingual support
const styles = StyleSheet.create({
    container: { 
        flex: 1, 
        backgroundColor: '#f5f5f5' 
    },
    loader: { 
        flex: 1, 
        justifyContent: 'center', 
        alignItems: 'center' 
    },
    itemContainer: { 
        backgroundColor: '#fff', 
        padding: 15, 
        marginVertical: 8, 
        marginHorizontal: 10, 
        borderRadius: 8, 
        elevation: 2, 
        shadowColor: '#000', 
        shadowOffset: { width: 0, height: 1 }, 
        shadowOpacity: 0.1, 
        shadowRadius: 2 
    },
    // Updated name styles for bilingual display
    nameContainer: {
        marginBottom: 10,
    },
    itemNamePrimary: { 
        fontSize: 17, 
        fontWeight: 'bold', 
        color: '#333', 
        marginBottom: 3,
    },
    itemNameSecondary: {
        fontSize: 14,
        fontWeight: '500',
        color: '#666',
        fontStyle: 'italic',
        textAlign: 'right', // Right-align Arabic text
    },
    itemInfoRow: { 
        flexDirection: 'row', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginTop: 10 
    },
    itemQuantity: { 
        fontSize: 15, 
        color: '#666' 
    },
    itemPrice: { 
        fontSize: 16, 
        fontWeight: '600', 
        color: '#000' 
    },
    itemDetailsRow: { 
        flexDirection: 'row', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginTop: 10 
    },
    quantityContainer: { 
        flexDirection: 'row', 
        alignItems: 'center', 
        backgroundColor: '#f0f0f0', 
        borderRadius: 5 
    },
    quantityButton: { 
        paddingHorizontal: 15, 
        paddingVertical: 5 
    },
    quantityButtonText: { 
        fontSize: 20, 
        fontWeight: 'bold', 
        color: '#007AFF' 
    },
    quantityText: { 
        fontSize: 16, 
        fontWeight: '600', 
        paddingHorizontal: 10 
    },
    removeButton: { 
        alignSelf: 'flex-end', 
        marginTop: 10, 
        padding: 5 
    },
    removeButtonText: { 
        color: 'red', 
        fontSize: 14 
    },
    footer: { 
        marginTop: 20, 
        padding: 15, 
        borderTopWidth: 1, 
        borderColor: '#e0e0e0', 
        backgroundColor: '#fff' 
    },
    totalText: { 
        fontSize: 20, 
        fontWeight: 'bold', 
        textAlign: 'right', 
        marginBottom: 15 
    },
    emptyText: { 
        textAlign: 'center', 
        marginTop: 50, 
        fontSize: 18, 
        color: '#888' 
    },
});

export default CartScreen;
