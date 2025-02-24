import React, { useState } from 'react';
import { QrReader } from 'react-qr-reader';

const Scan = () => {
    const [result, setResult] = useState<string | null>(null);

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold">Scanner un QR Code</h1>
            <QrReader
                onResult={(result, error) => {
                    if (result) {
                        setResult(result.getText());
                    }
                    if (error) {
                        console.error(error);
                    }
                }
            }
                style={{ width: '100%' }}
            />
            {result && <p>Résultat : {result}</p>}
        </div>
    );
};

export default Scan;
