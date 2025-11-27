import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Recommendations() {
    const [recommendations, setRecommendations] = useState([]);
    const [userId, setUserId] = useState('1');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [apiStatus, setApiStatus] = useState('');

    const fetchRecommendations = async (id) => {
        setLoading(true);
        setError(null);
        setApiStatus('');

        try {
            const response = await axios.get(`http://localhost:5000/recommend/${id}`);
            setRecommendations(response.data.recommendations);
            setApiStatus(response.data.status);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            setError('Failed to fetch recommendations. Please try again.');
            setRecommendations([]);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'als_recommendations': return 'text-green-600';
            case 'fallback_recommendations': return 'text-yellow-600';
            default: return 'text-gray-600';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'als_recommendations': return 'AI Recommendations';
            case 'fallback_recommendations': return 'Fallback Recommendations';
            default: return status;
        }
    };

    useEffect(() => {
        fetchRecommendations(userId);
    }, []);

    return (
        <div className="p-6 max-w-2xl mx-auto bg-white rounded-xl shadow-lg">
            <div className="text-center mb-6">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">🎬 Movie Recommender</h1>
                <p className="text-gray-600">Get personalized movie recommendations</p>
            </div>

            {/* User Input Section */}
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <div className="flex flex-col sm:flex-row gap-3">
                    <input
                        type="text"
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        className="flex-1 border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter User ID (1-100)"
                    />
                    <button
                        onClick={() => fetchRecommendations(userId)}
                        disabled={loading}
                        className="bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600 disabled:bg-blue-300 transition-colors font-medium"
                    >
                        {loading ? 'Loading...' : 'Get Recommendations'}
                    </button>
                </div>

                {apiStatus && (
                    <div className={`mt-3 text-sm font-medium ${getStatusColor(apiStatus)}`}>
                        Status: {getStatusText(apiStatus)}
                    </div>
                )}
            </div>

            {/* Error Message */}
            {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    {error}
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    <p className="mt-2 text-gray-600">Finding your perfect movies...</p>
                </div>
            )}

            {/* Recommendations List */}
            {!loading && recommendations.length > 0 && (
                <div>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800">
                        Recommended Movies ({recommendations.length})
                    </h2>
                    <div className="space-y-3">
                        {recommendations.map((movie, index) => (
                            <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:bg-white transition-colors">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="font-semibold text-gray-800">{movie.title}</h3>
                                        <p className="text-sm text-gray-600 mt-1">Movie ID: {movie.movie_id}</p>
                                        {movie.genres && movie.genres !== "Unknown" && (
                                            <p className="text-sm text-blue-600 mt-1">Genres: {movie.genres}</p>
                                        )}
                                    </div>
                                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                                        #{index + 1}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!loading && recommendations.length === 0 && !error && (
                <div className="text-center py-8 text-gray-500">
                    No recommendations found. Try a different User ID.
                </div>
            )}
        </div>
    );
}

export default Recommendations;