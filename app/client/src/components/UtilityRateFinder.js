import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import {
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  Typography,
  Alert,
  Box,
  Paper,
  CircularProgress,
  Container,
  Snackbar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tab,
  Tabs
} from '@mui/material';

const UtilityRateFinder = () => {
  const [formData, setFormData] = useState({
    address: '',
    consumption: 1000,
    escalator: 4,
    selectedRate: ''
  });
  
  const [utilityData, setUtilityData] = useState({
    rates: [],
    mostLikelyRate: null,
    selectedRate: null,
    yearlyCosts: [],
    loading: false,
    error: null
  });
  
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  const [viewMode, setViewMode] = useState('graph');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUtilityData(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch('/api/utility-rates/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(formData),
        credentials: 'same-origin'
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch utility rates');
      }

      const data = await response.json();
      setUtilityData({
        rates: data.rates || [],
        mostLikelyRate: data.most_likely_rate,
        selectedRate: data.selected_rate,
        yearlyCosts: data.yearly_costs || [],
        loading: false,
        error: null
      });

      setSnackbar({
        open: true,
        message: 'Utility rates retrieved successfully!',
        severity: 'success'
      });
    } catch (error) {
      setUtilityData(prev => ({
        ...prev,
        loading: false,
        error: error.message
      }));
      
      setSnackbar({
        open: true,
        message: error.message,
        severity: 'error'
      });
    }
  };

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const prepareChartData = () => {
    return utilityData.yearlyCosts.map((cost, index) => {
      const cumulativeCost = utilityData.yearlyCosts
        .slice(0, index + 1)
        .reduce((sum, c) => sum + c, 0);
      return {
        year: `Year ${index + 1}`,
        annualCost: cost,
        cumulativeCost: cumulativeCost
      };
    });
  };

  const renderProjectionContent = () => {
    if (utilityData.yearlyCosts.length === 0) return null;

    const chartData = prepareChartData();

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

        {viewMode === 'graph' && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart 
                  data={chartData} 
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="year" 
                    angle={-45}
                    textAnchor="end"
                    height={70}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    tickFormatter={(value) => formatCurrency(value)}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip 
                    formatter={(value) => formatCurrency(value)}
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                      padding: '10px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="annualCost"
                    name="Annual Cost"
                    stroke="#2196f3"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="cumulativeCost"
                    name="Cumulative Cost"
                    stroke="#f50057"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        )}

        {viewMode === 'table' && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Year</TableCell>
                  <TableCell align="right">Annual Cost</TableCell>
                  <TableCell align="right">Cumulative Cost</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {chartData.map((row, index) => (
                  <TableRow key={index}>
                    <TableCell>{row.year}</TableCell>
                    <TableCell align="right">{formatCurrency(row.annualCost)}</TableCell>
                    <TableCell align="right">{formatCurrency(row.cumulativeCost)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom>
            Utility Rate Calculator
          </Typography>

          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'grid', gap: 3, mb: 4 }}>
              <TextField
                fullWidth
                label="US Address"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
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
                onChange={handleInputChange}
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
                onChange={handleInputChange}
                required
                inputProps={{ min: 4, max: 10, step: 0.1 }}
                helperText="Enter a value between 4% and 10%"
                variant="outlined"
              />

              {utilityData.rates.length > 0 && (
                <FormControl fullWidth>
                  <InputLabel>Select Rate Plan</InputLabel>
                  <Select
                    name="selectedRate"
                    value={formData.selectedRate}
                    onChange={handleInputChange}
                    label="Select Rate Plan"
                  >
                    {utilityData.rates.map((rate) => (
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
                disabled={utilityData.loading}
                sx={{ height: 56 }}
              >
                {utilityData.loading ? (
                  <CircularProgress size={24} sx={{ color: 'white' }} />
                ) : (
                  'Calculate Rates'
                )}
              </Button>
            </Box>
          </form>

          {utilityData.error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {utilityData.error}
            </Alert>
          )}

          {utilityData.selectedRate && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Selected Rate Plan
              </Typography>
              <Paper sx={{ p: 2 }}>
                <Typography>
                  Utility: {utilityData.selectedRate.utility}
                </Typography>
                <Typography>
                  Plan: {utilityData.selectedRate.name}
                </Typography>
                <Typography>
                  Average Rate: {utilityData.selectedRate.avg_rate.toFixed(2)}¢/kWh
                </Typography>
                <Typography>
                  First Year Cost: {formatCurrency(utilityData.yearlyCosts[0])}
                </Typography>
              </Paper>
            </Box>
          )}

          {renderProjectionContent()}
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default UtilityRateFinder;