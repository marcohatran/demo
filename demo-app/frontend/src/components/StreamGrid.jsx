import React from 'react';
import StreamCard from './StreamCard';

const StreamGrid = ({ subtitle }) => {
    return (
        <div className="h-full">
            <StreamCard
                source="Euronews Live"
                subtitle={subtitle}
            />
        </div>
    );
};

export default StreamGrid;
