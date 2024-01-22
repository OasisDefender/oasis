export interface IIntercomSettings {
    appID: string;
    apiBase?: string;
    email?: string;
    userHash?: string;
}

export interface IInitSettings {
    intercomSettings?: IIntercomSettings;
}