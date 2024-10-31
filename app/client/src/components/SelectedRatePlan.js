import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { formatCurrency } from '../utils/formatters';

export const SelectedRatePlan = ({ selectedRate, firstYearCost }) => {
  if (!selectedRate) return null;

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Selected Rate Plan
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography>Utility: {selectedRate.utility}</Typography>
        <Typography>Plan: {selectedRate.name}</Typography>
        <Typography>
          Average Rate: {selectedRate.avg_rate.toFixed(2)}¢/kWh
        </Typography>
        <Typography>
          First Year Cost: {formatCurrency(firstYearCost)}
        </Typography>
      </Paper>
    </Box>
  );
};
