// VOCERY/frontend/src/screens/ProductDetailScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert, Image, ScrollView, Button } from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App'; // Adjust path if needed

// We can reuse the Product type, but for detail, it might have more fields
// Or it could be the same. Let's define it here for clarity.
type Product = {
    product_id: number;
    name_en: string;
    description_en: string;
    price: number;
    image_url?: string;
    brand?: string;
    stock_quantity?: number;
};

// Define props type for this screen, specifying it receives 'productId'
type ProductDetailScreenProps = StackScreenProps<RootStackParamList, 'ProductDetail'>;

const ProductDetailScreen = ({ route, navigation }: ProductDetailScreenProps) => {
    // Get productId from the parameters passed during navigation
    const { productId } = route.params;
    const [quantity, setQuantity] = useState<number>(1);
    const [product, setProduct] = useState<Product | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchProductDetails = async () => {
            if (!productId) {
                Alert.alert("Error", "No product ID provided.");
                navigation.goBack();
                return;
            }

            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) {
                    Alert.alert("Authentication Error", "Please log in again.");
                    navigation.replace('Login');
                    return;
                }

                // Fetch details for the specific product ID
                const response = await axios.get(`http://10.0.2.2:5000/api/products/${productId}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setProduct(response.data);
            } catch (error: any) {
                console.error("Failed to fetch product details:", error.message);
                Alert.alert("Error", "Could not load product details.");
            } finally {
                setLoading(false);
            }
        };

        fetchProductDetails();
    }, [productId, navigation]); // Re-run effect if productId or navigation changes

    const handleAddToCart = async () => {
        if (!product) return;
        try {
            const token = await AsyncStorage.getItem('userToken');
            if (!token) {
                Alert.alert("Please log in", "You need to be logged in to add items to your cart.");
                navigation.replace('Login');
                return;
            }

            // Make the API call to add the item
            await axios.post('http://10.0.2.2:5000/api/cart/add',
                {
                    product_id: product.product_id,
                    quantity: quantity,
                },
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            Alert.alert("Success", `${quantity} x ${product.name_en} added to cart!`);
            // Optionally, navigate to the cart screen
            // navigation.navigate('Cart');

        } catch (error: any) {
            console.error("Failed to add to cart:", error.response?.data || error.message);
            Alert.alert("Error", `Could not add item to cart. ${error.response?.data?.error || ''}`);
        }
    };  

    // Show a loading indicator while fetching data
    if (loading) {
        return (
            <View style={styles.loader}>
                <ActivityIndicator size="large" color="#007AFF" />
            </View>
        );
    }

    // Show a message if the product could not be found
    if (!product) {
        return (
            <View style={styles.container}>
                <Text style={styles.errorText}>Product not found.</Text>
                <Button title="Go Back" onPress={() => navigation.goBack()} />
            </View>
        );
    }

    // Render the product details
    return (
        <ScrollView style={styles.container}>
            {product.image_url ? (
                <Image style={styles.image} source={{ uri: product.image_url }} />
            ) : (
                <View style={[styles.image, styles.imagePlaceholder]}>
                    <Text>No Image</Text>
                </View>
            )}
            <View style={styles.infoContainer}>
                <Text style={styles.brand}>{product.brand || 'Generic'}</Text>
                <Text style={styles.name}>{product.name_en}</Text>
                <Text style={styles.price}>${product.price.toFixed(2)}</Text>
                <Text style={styles.description}>{product.description_en}</Text>

                <View style={styles.stockInfo}>
                    <Text>In Stock: {product.stock_quantity || 0}</Text>
                </View>
                
                <View style={styles.quantityContainer}>
                <Button title="-" onPress={() => setQuantity(q => Math.max(1, q - 1))} />
                <Text style={styles.quantityText}>{quantity}</Text>
                <Button title="+" onPress={() => setQuantity(q => q + 1)} />
                </View>

                <View style={styles.buttonContainer}>
                <Button title={`Add ${quantity} to Cart`} onPress={handleAddToCart} />
                </View>
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
    },
    loader: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    errorText: {
        textAlign: 'center',
        marginTop: 20,
        fontSize: 18,
        color: 'red',
    },
    image: {
        width: '100%',
        aspectRatio: 1, // Keep it square
        resizeMode: 'contain',
    },
    imagePlaceholder: {
        backgroundColor: '#eee',
        justifyContent: 'center',
        alignItems: 'center',
    },
    infoContainer: {
        padding: 20,
    },
    brand: {
        fontSize: 16,
        color: '#888',
        marginBottom: 5,
    },
    name: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 10,
    },
    price: {
        fontSize: 22,
        color: 'green',
        fontWeight: '600',
        marginBottom: 20,
    },
    description: {
        fontSize: 16,
        color: '#555',
        lineHeight: 24,
        marginBottom: 20,
    },
    stockInfo: {
        paddingVertical: 10,
        borderTopWidth: 1,
        borderBottomWidth: 1,
        borderColor: '#eee',
        marginBottom: 20,
    },
    buttonContainer: {
        marginTop: 10,
    },
     quantityContainer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        marginVertical: 20,
    },
    quantityText: {
        fontSize: 20,
        fontWeight: 'bold',
        marginHorizontal: 20,
    },
});

export default ProductDetailScreen;