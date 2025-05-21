export const generateKeyPair = async (): Promise<string> => {
  const keyPair = await window.crypto.subtle.generateKey(
    {
      name: 'RSA-OAEP',
      modulusLength: 2048,
      publicExponent: new Uint8Array([1, 0, 1]),
      hash: 'SHA-256',
    },
    true,
    ['encrypt', 'decrypt']
  );

  const publicKey = await window.crypto.subtle.exportKey('spki', keyPair.publicKey);
  const privateKey = await window.crypto.subtle.exportKey('pkcs8', keyPair.privateKey);

  const exportedPublicKey = btoa(String.fromCharCode(...new Uint8Array(publicKey)));
  const exportedPrivateKey = btoa(String.fromCharCode(...new Uint8Array(privateKey)));

  localStorage.setItem('private_key', exportedPrivateKey);

  return exportedPublicKey;
};
