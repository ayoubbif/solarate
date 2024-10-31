import React, { useState } from 'react';
import { Box, Typography, Tabs, Tab } from '@mui/material';
import {CostProjectionChart} from './CostProjectionChart';
import {CostProjectionTable} from './CostProjectionTable';

export const CostProjection = ({ yearlyCosts }) => {
    const [viewMode, setViewMode] = useState('graph');
  
    if (yearlyCosts.length === 0) return null;
  
    const chartData = yearlyCosts.map((cost, index) => {
      const cumulativeCost = yearlyCosts
        .slice(0, index + 1)
        .reduce((sum, c) => sum + c, 0);
      return {
        year: `Year ${index + 1}`,
        annualCost: cost,
        cumulativeCost: cumulativeCost
      };
    });
  
    return (
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          20 Year Cost Projection
        </Typography>
        
        <Box sx={{ mb: 4 }}>
          <Tabs 
            value={viewMode} 
            onChange={(_, newValue) => setViewMode(newValue)}
            sx={{ mb: 2 }}
          >
            <Tab value="graph" label="Graph View" />
            <Tab value="table" label="Table View" />
          </Tabs>
        </Box>
  
        {viewMode === 'graph' ? (
          <CostProjectionChart chartData={chartData} />
        ) : (
          <CostProjectionTable chartData={chartData} />
        )}
      </Box>
    );
  };