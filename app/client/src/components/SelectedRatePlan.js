import React from 'react';
import { Box, Typography, Paper, Skeleton } from '@mui/material';
import { formatCurrency } from '../utils/formatters';

export const SelectedRatePlan = ({
  selectedRate,
  firstYearCost,
  isLoading
}) => {
  if (!selectedRate && !isLoading) return null;

  if (isLoading) {
    return (
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Selected Rate Plan
        </Typography>
        <Paper sx={{ p: 2 }}>
          <Skeleton width="60%" />
          <Skeleton width="40%" />
          <Skeleton width="50%" />
          <Skeleton width="45%" />
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Selected Rate Plan
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>Utility:</strong> {selectedRate.utility}
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>Plan:</strong> {selectedRate.name}
        </Typography>
        <Typography variant="body1" sx={{ mb: 1 }}>
          <strong>Average Rate:</strong> {selectedRate.avg_rate.toFixed(2)}¢/kWh
        </Typography>
        <Typography variant="body1">
          <strong>First Year Cost:</strong> {formatCurrency(firstYearCost)}
        </Typography>
      </Paper>
    </Box>
  );
};
