import { createContext } from 'react';
import { IInitSettings } from '../models/IInitSettings';

const InitSettingsContext = createContext<IInitSettings>({});

export default InitSettingsContext;
