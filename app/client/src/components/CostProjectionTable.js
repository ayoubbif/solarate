import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { formatCurrency } from '../utils/formatters';

export const CostProjectionTable = ({ chartData }) => (
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
  );