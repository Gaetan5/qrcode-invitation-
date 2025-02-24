import React, { useState } from 'react';

const Billet = () => {
    const [qrCode, setQrCode] = useState<string | null>(null);
    
    const generateQr = async () => {
        const response = await fetch('http://localhost:5000/generate_qr', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: 'Exemple de billet' })
        });
        const result = await response.json();
        setQrCode(result.qr_code);
    };

    return (
        <div className="p-4">
            <button className="bg-blue-500 text-white px-4 py-2" onClick={generateQr}>Générer un QR Code</button>
            {qrCode && <img src={`data:image/png;base64,${qrCode}`} alt="QR Code" />}
        </div>
    );
};

export default Billet;
