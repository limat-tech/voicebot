import React, { useState, useEffect, useLayoutEffect } from 'react';
import {
    View,
    Text,
    FlatList,
    StyleSheet,
    ActivityIndicator,
    TouchableOpacity,
    Alert,
    TextInput,
    Platform,
    PermissionsAndroid
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import type { StackScreenProps } from '@react-navigation/stack';
import type { RootStackParamList } from '../../App';

const audioRecorderPlayer = new AudioRecorderPlayer();

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
    const [isRecording, setIsRecording] = useState(false);
    const [statusMessage, setStatusMessage] = useState('Tap microphone to speak');

    const requestPermissions = async () => {
        if (Platform.OS === 'android') {
            try {
                const granted = await PermissionsAndroid.request(
                    PermissionsAndroid.PERMISSIONS.RECORD_AUDIO
                );
                if (granted === PermissionsAndroid.RESULTS.GRANTED) {
                    console.log('RECORD_AUDIO permission granted');
                    return true;
                } else {
                    console.log('RECORD_AUDIO permission denied');
                    return false;
                }
            } catch (err) {
                console.warn('Permission request error:', err);
                return false;
            }
        }
        return true;
    };

    const startRecording = async () => {
        const hasPermission = await requestPermissions();
        if (!hasPermission) {
            Alert.alert('Permission Required', 'Microphone permission is needed to record audio.');
            return;
        }
        setIsRecording(true);
        setStatusMessage('Recording...');
        try {
            const result = await audioRecorderPlayer.startRecorder();
            audioRecorderPlayer.addRecordBackListener((e) => {
                setStatusMessage(`Recording... ${e.currentPosition.toFixed(1)}s`);
                return;
            });
            console.log(`Recording started: ${result}`);
        } catch (e) {
            console.error('Failed to start recording', e);
            setStatusMessage('Error: Could not start recording');
            setIsRecording(false);
        }
    };

    const stopRecording = async () => {
        setIsRecording(false);
        setStatusMessage('Processing...');
        try {
            const resultPath = await audioRecorderPlayer.stopRecorder();
            audioRecorderPlayer.removeRecordBackListener();
            console.log(`Recording stopped. File is at: ${resultPath}`);
            handleVoiceUpload(resultPath);
        } catch (e) {
            console.error('Failed to stop recording', e);
            setStatusMessage('Error: Could not save recording');
        }
    };

    const handleVoiceUpload = async (filePath: string) => {
        const formData = new FormData();
        const fileUri = Platform.OS === 'android' ? `file://${filePath}` : filePath;
        formData.append('audio', {
            uri: fileUri,
            type: 'audio/mp4',
            name: 'voice_command.mp4',
        });
        try {
            const API_URL = 'http://10.0.2.2:5000/api/voice/process';
            console.log(`Uploading audio from URI: ${fileUri}`);
            const response = await axios.post(API_URL, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            console.log('Full AI Pipeline Response:', response.data);
            const { transcript, intent, entities } = response.data;
            setStatusMessage(`Heard: "${transcript}"`);
            if (intent === 'search_product' && entities && entities.length > 0) {
                setSearchTerm(entities[0].value);
            }
        } catch (error) {
            console.error('Error uploading audio:', error);
            setStatusMessage('Error: Could not process request.');
        }
    };

    useLayoutEffect(() => {
        navigation.setOptions({
            headerRight: () => (
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
    }, [navigation]);

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
                placeholder="Search or use voice..."
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
            
            <View style={styles.voiceContainer}>
                <TouchableOpacity 
                    onPress={isRecording ? stopRecording : startRecording} 
                    style={[styles.micButton, isRecording && styles.micButtonActive]}
                >
                    <Text style={styles.micButtonText}>
                        {isRecording ? 'STOP' : 'MIC'}
                    </Text>
                </TouchableOpacity>
                
                <Text style={styles.voiceStatusText}>{statusMessage}</Text>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f8f8',
    },
    headerRightContainer: {
        flexDirection: 'row',
        marginRight: 10,
    },
    headerButton: {
        marginLeft: 15,
    },
    headerButtonText: {
        color: '#fff',
        fontSize: 16,
    },
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
        paddingBottom: 150,
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
    voiceContainer: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: 20,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
        alignItems: 'center',
    },
    micButton: {
        width: 70,
        height: 70,
        borderRadius: 35,
        backgroundColor: '#007AFF',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 10,
        elevation: 5,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
    },
    micButtonActive: {
        backgroundColor: '#FF3B30',
    },
    micButtonText: {
        fontSize: 16,
        fontWeight: 'bold',
        color: 'white',
    },
    voiceStatusText: {
        fontSize: 14,
        color: '#666',
        textAlign: 'center',
        fontStyle: 'italic',
    },
});

export default ProductListScreen;