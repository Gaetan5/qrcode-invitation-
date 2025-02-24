import React from 'react';
import Link from 'next/link';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-8">
      <div className="container mx-auto text-center">
        <p>&copy; {new Date().getFullYear()} Your Company Name. All rights reserved.</p>
        <div className="mt-4">
          <Link href="/">
            <a className="text-white hover:text-gray-300 mx-2">Home</a>
          </Link>
          <Link href="/about">
            <a className="text-white hover:text-gray-300 mx-2">About</a>
          </Link>
          <Link href="/contact">
            <a className="text-white hover:text-gray-300 mx-2">Contact</a>
          </Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
