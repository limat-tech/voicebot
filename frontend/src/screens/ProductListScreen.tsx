// VOCERY/frontend/src/screens/ProductListScreen.tsx
import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    ActivityIndicator,
    TouchableOpacity,
    Alert
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App'; // Adjust path if needed

// Define a type for your product data
type Product = {
    product_id: number; // CORRECTED: Changed from productid to product_id
    name_en: string;    // Assuming name_en from your log
    name_ar?: string;   // Assuming name_ar
    price: number;
    brand?: string;
    category_id?: number;
    description_ar?: string;
    description_en?: string;
    image_url?: string;
    stock_quantity?: number;
    unit_type?: string;
    // Add other product fields as defined in your API response, matching case
};
type ProductListScreenProps = StackScreenProps<RootStackParamList, 'ProductList'>;

const ProductListScreen = ({ navigation }: ProductListScreenProps) => {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) {
                    Alert.alert("Authentication Error", "No token found. Please log in again.");
                    navigation.replace('Login');
                    return;
                }

                const response = await axios.get('http://10.0.2.2:5000/api/products', { // Ensure this URL is correct
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                
                const fetchedProducts = response.data.products || response.data;
                if (Array.isArray(fetchedProducts)) {
                    setProducts(fetchedProducts);
                } else {
                    console.error("Fetched products is not an array:", fetchedProducts);
                    setProducts([]);
                }

            } catch (error: any) {
                console.error('Failed to fetch products:', error.response?.data || error.message);
                Alert.alert(
                    'Error',
                    `Failed to fetch products: ${error.response?.data?.error || error.message}`
                );
                if (error.response?.status === 401) {
                    navigation.replace('Login');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, [navigation]);

    const renderItem = ({ item }: { item: Product }) => (
        <TouchableOpacity 
            style={styles.itemContainer}
            // Placeholder action, will be updated for ProductDetail screen
            onPress={() => Alert.alert("Product Clicked", `You clicked on ${item.name_en}`)}
        >
            <Text style={styles.itemName}>{item.name_en}</Text>
            <Text style={styles.itemPrice}>Price: ${item.price ? item.price.toFixed(2) : 'N/A'}</Text>
            {/* You can add item.brand here if you want */}
        </TouchableOpacity>
    );

    // Removed the extra console.log for products here as you've provided the output

    if (loading) {
        return (
            <View style={styles.loader}>
                <ActivityIndicator size="large" color="#0000ff" />
                <Text>Loading products...</Text>
            </View>
        );
    }

    return (
        <FlatList
            data={products}
            renderItem={renderItem}
            keyExtractor={(item, index) => {
                // Accessing item.product_id (snake_case)
                if (item && item.product_id != null) { // CORRECTED: Changed to product_id
                    return item.product_id.toString();
                }
                // Fallback if product_id is missing
                console.warn(`Product at index ${index} is missing a product_id or item is null/undefined:`, item);
                return `product-fallback-${index}`; 
            }}
            contentContainerStyle={styles.listContainer}
            ListEmptyComponent={
                <View style={styles.emptyContainer}>
                    <Text style={styles.emptyText}>No products found.</Text>
                </View>
            }
        />
    );
};

const styles = StyleSheet.create({
    listContainer: {
        paddingHorizontal: 10,
        paddingBottom: 10,
    },
    loader: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    itemContainer: {
        backgroundColor: '#fff',
        padding: 15,
        marginVertical: 8,
        borderRadius: 8,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.2,
        shadowRadius: 1.41,
    },
    itemName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
    },
    itemPrice: {
        fontSize: 16,
        color: 'green',
        marginTop: 5,
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

export default ProductListScreen;
