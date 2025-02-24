import React from 'react';
import QRCode from 'qrcode.react';

const QrcodeDisplay = ({ qrCodeData }) => {
  return (
    <div>
      {qrCodeData && (
        <QRCode value={qrCodeData} size={256} level="H" />
      )}
    </div>
  );
};

export default QrcodeDisplay;
