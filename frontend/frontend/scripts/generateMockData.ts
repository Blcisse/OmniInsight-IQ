import fs from 'fs';
const salesData = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  product: `Product ${i + 1}`,
  unitsSold: Math.floor(Math.random() * 500),
  revenue: +(Math.random() * 10000).toFixed(2),
}));
fs.writeFileSync('src/app/dashboard/data/salesData.json', JSON.stringify(salesData, null, 2));
console.log('Mock sales data generated!');
