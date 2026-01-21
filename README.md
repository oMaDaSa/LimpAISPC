# LimpAI SPC

An intelligent debt analysis tool, to help Brazilian consumers understand their credit contracts, identify abusive interest rates, and provides AI-powered legal insights based on Brazilian consumer protection laws.

## Features

- **Market Rate Comparison**: Fetches market rates from Brazilian Central Bank (BCB) API
- **AI-Powered Legal Insights**: Uses AI to generate detailed reports
- **Consumer Protection**: Identifies potential violations of Brazilian consumer protection laws
- **Multiple Credit Types Support**:
  - Credit Card (Revolving & Installment)
  - Personal Loans (Secured & Unsecured)
  - Vehicle Financing
  - Special Check (Cheque Especial)
  - And more

## Structure

```
LimpAI SPC/
├── backend/                   
│   ├── lambda_function.py     # AWS Lambda entry point
│   ├── requirements_local.txt # Local development dependencies
│   ├── requirements_layer.txt # AWS Lambda layer dependencies
│   └── src/
│       ├── app.py            # Flask application
│       ├── api/
│       │   └── routes.py     # API endpoints
│       ├── core/
│       │   └── config.py     # Configuration settings
│       └── services/
│           ├── calculator.py     # Financial calculations
│           ├── data_parser.py    # Data parsing utilities
│           └── debt_analysis.py  # Core analysis logic
└── docs/                      #frontend            
    ├── index.html            
    ├── app.js                
    └── styles.css       
```

## Technologies

### Backend
- **Python**
- **Flask** - Web framework
- **AWS Lambda** - Serverless functions
- **AWS API Gateway** - RESTful API management and routing
- **AWS Bedrock and Knowledge Base** - AI model integration

## Installation

**Configure environment variables**

**Update the frontend to use localhost**
In `docs/app.js`, comment out the AWS endpoint and uncomment the localhost line:
```javascript
// const response = await fetch('https://7z59i92b98.execute-api.us-east-1.amazonaws.com/api/debt-analysis', {
const response = await fetch('http://localhost:5000/api/debt-analysis', {
```

**Run the backend locally**
The backend will start on `http://localhost:5000`

**Run the frontend**
Simply open `docs/index.html` in your browser

## Configuration

### Backend Configuration

Edit `backend/src/core/config.py` to customize:
- API settings
- AWS configurations
- Database connections (if applicable)
- AI model parameters

## API Documentation

### Endpoint: `/api/debt-analysis`

**Method**: POST

**Request Body**:
```json
{
  "nome": "Client Name",
  "serie_bcb": "20716",
  "data_contrato": "15/01/2025",
  "taxa_cet": 12.5,
  "renda": 3000.00,
  "parcela": 250.00,
  "valor_total_emprestimo": 5000.00,
  "quantidade_parcelas": 24,
  "quantidade_dependentes": 2,
  "valor_cesta_basica": 700.00,
  "taxa_mercado_anual": 23.82,
  "password": "your_password"
}
```

**Response**:
```json
{
  "status": "success",
  "ai_response": "# Detailed Analysis in Markdown format ..."
}
```

This is a personal project. If you'd like to contribute or test the application, please contact:
- **LinkedIn**: [Matheus Santana](https://www.linkedin.com/in/matheusdsantana/)
- **Email**: matheusdsantna07@gmail.com

## Legal Disclaimer

This tool provides educational information and preliminary analysis. It does NOT replace professional legal advice.

This project is for educational and demonstration purposes. All rights reserved.

---