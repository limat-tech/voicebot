// VOCERY/frontend/src/screens/ProductListScreen.tsx
import React, { useState, useEffect, useLayoutEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    ActivityIndicator,
    TouchableOpacity,
    Alert,
    TextInput
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App'; // Adjust path if needed

// Your Product type definition
type Product = {
    product_id: number;
    name_en: string;
    name_ar?: string;
    price: number;
    brand?: string;
    category_id?: number;
    description_ar?: string;
    description_en?: string;
    image_url?: string;
    stock_quantity?: number;
    unit_type?: string;
};

type ProductListScreenProps = StackScreenProps<RootStackParamList, 'ProductList'>;

const ProductListScreen = ({ navigation }: ProductListScreenProps) => {
    const [products, setProducts] = useState<Product[]>([]);
    const [originalProducts, setOriginalProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [searchTerm, setSearchTerm] = useState<string>('');

    // --- FIX IS HERE ---
    // Combine both header buttons into a single useLayoutEffect call
    useLayoutEffect(() => {
        navigation.setOptions({
            headerRight: () => (
                // Wrap both buttons in a single View
                <View style={styles.headerRightContainer}>
                    <TouchableOpacity onPress={() => navigation.navigate('Cart')} style={styles.headerButton}>
                        <Text style={styles.headerButtonText}>Cart</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => navigation.navigate('Profile')} style={styles.headerButton}>
                        <Text style={styles.headerButtonText}>Profile</Text>
                    </TouchableOpacity>
                </View>
            ),
        });
    }, [navigation]);

    // Effect for the initial load of all products
    useEffect(() => {
        const loadInitialData = async () => {
            setLoading(true);
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) {
                    navigation.replace('Login');
                    return;
                }
                const response = await axios.get('http://10.0.2.2:5000/api/products', {
                    headers: { Authorization: `Bearer ${token}` },
                });
                const fetchedProducts = response.data.products || response.data;
                if (Array.isArray(fetchedProducts)) {
                    setProducts(fetchedProducts);
                    setOriginalProducts(fetchedProducts);
                }
            } catch (error) {
                console.error('Failed to fetch initial products:', error);
            } finally {
                setLoading(false);
            }
        };
        loadInitialData();
    }, []);

    // Effect for handling search
    useEffect(() => {
        if (searchTerm.trim() === '') {
            setProducts(originalProducts);
            return;
        }
        const handleSearch = async () => {
            try {
                const token = await AsyncStorage.getItem('userToken');
                if (!token) { return; }
                const response = await axios.get(`http://10.0.2.2:5000/api/products/search?q=${encodeURIComponent(searchTerm)}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setProducts(response.data.products || response.data);
            } catch (error) {
                console.error("Search failed:", error);
                setProducts([]);
            }
        };
        const delayDebounceFn = setTimeout(() => {
            handleSearch();
        }, 300);
        return () => clearTimeout(delayDebounceFn);
    }, [searchTerm, originalProducts]);

    const renderItem = ({ item }: { item: Product }) => (
        <TouchableOpacity
            style={styles.itemContainer}
            onPress={() => navigation.navigate('ProductDetail', { productId: item.product_id })}
        >
            <Text style={styles.itemName}>{item.name_en}</Text>
            <Text style={styles.itemPrice}>Price: ${item.price ? item.price.toFixed(2) : 'N/A'}</Text>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <TextInput
                style={styles.searchInput}
                placeholder="Search for products..."
                value={searchTerm}
                onChangeText={setSearchTerm}
                clearButtonMode="while-editing"
            />
            {loading ? (
                <ActivityIndicator size="large" color="#0000ff" style={{ marginTop: 20 }} />
            ) : (
                <FlatList
                    data={products}
                    renderItem={renderItem}
                    keyExtractor={(item) => item.product_id.toString()}
                    contentContainerStyle={styles.listContainer}
                    ListEmptyComponent={
                        <View style={styles.emptyContainer}>
                            <Text style={styles.emptyText}>No products found.</Text>
                        </View>
                    }
                />
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    // --- ADDED STYLES FOR HEADER BUTTONS ---
    headerRightContainer: {
        flexDirection: 'row',
        marginRight: 10,
    },
    headerButton: {
        marginLeft: 15, // Space between buttons
    },
    headerButtonText: {
        color: '#fff',
        fontSize: 16,
    },
    // ---
    searchInput: {
        height: 45,
        borderColor: '#ddd',
        borderWidth: 1,
        borderRadius: 8,
        paddingHorizontal: 15,
        margin: 10,
        backgroundColor: '#fff',
        fontSize: 16,
    },
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