import React from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';

export const UtilityForm = ({
  formData,
  onInputChange,
  onSubmit,
  loading,
  rates
}) => {
  return (
    <form onSubmit={onSubmit}>
      <Box sx={{ display: 'grid', gap: 3, mb: 4 }}>
        <TextField
          fullWidth
          label="US Address"
          name="address"
          value={formData.address}
          onChange={onInputChange}
          required
          placeholder="Enter your complete address"
          variant="outlined"
        />

        <TextField
          fullWidth
          label="Annual Consumption (kWh)"
          name="consumption"
          type="number"
          value={formData.consumption}
          onChange={onInputChange}
          required
          inputProps={{ min: 1000, max: 10000 }}
          helperText="Enter a value between 1,000 and 10,000 kWh"
          variant="outlined"
        />

        <TextField
          fullWidth
          label="Escalator Rate (%)"
          name="escalator"
          type="number"
          value={formData.escalator}
          onChange={onInputChange}
          required
          inputProps={{ min: 4, max: 10, step: 0.1 }}
          helperText="Enter a value between 4% and 10%"
          variant="outlined"
        />

        {rates.length > 0 && (
          <FormControl fullWidth>
            <InputLabel>Select Rate Plan</InputLabel>
            <Select
              name="selectedRate"
              value={formData.selectedRate}
              onChange={onInputChange}
              label="Select Rate Plan"
            >
              {rates.map((rate) => (
                <MenuItem key={rate.label} value={rate.label}>
                  {rate.utility} - {rate.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={loading}
          sx={{ height: 56 }}
        >
          {loading ? (
            <CircularProgress size={24} sx={{ color: 'white' }} />
          ) : (
            'Calculate Rates'
          )}
        </Button>
      </Box>
    </form>
  );
};
