import axios from 'axios';
import config from '../config';

export const fetchCentrifugoToken = (token: string) =>
  axios.get(`${config.apiBaseUrl}/message/centrifugo/token`, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const getCentrifugoWsUrl = () => config.centrifugoWsUrl;
