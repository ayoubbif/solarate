import React from 'react';
import { Snackbar, Alert } from '@mui/material';

export const FeedbackSnackbar = ({ open, message, severity, onClose }) => (
  <Snackbar open={open} autoHideDuration={6000} onClose={onClose}>
    <Alert
      onClose={onClose}
      severity={severity}
      variant="filled"
      sx={{ width: '100%' }}
    >
      {message}
    </Alert>
  </Snackbar>
);
