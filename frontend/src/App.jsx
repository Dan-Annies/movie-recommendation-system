import React from 'react';
import Recommendations from './components/Recommendations';

export default function App() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
            <div className="container mx-auto px-4">
                <Recommendations />
            </div>
        </div>
    );
}