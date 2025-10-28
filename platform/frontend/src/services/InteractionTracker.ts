/**
 * 🤖 ML System: Serviço de Rastreamento de Interações
 * 
 * Captura interações dos usuários com veículos para treinamento
 * de modelos de Machine Learning.
 * 
 * Características:
 * - Não bloqueia UI em caso de falhas
 * - Gerencia session_id anônimo no localStorage
 * - Envia dados de forma assíncrona
 * - Respeita privacidade (dados anônimos)
 * 
 * @author AI Engineer
 * @date Outubro 2024
 */

import axios from 'axios';

// Tipos de interação
export type InteractionType = 'click' | 'view_details' | 'whatsapp_contact';

// Interface para preferências do usuário
export interface UserPreferences {
    budget: number;
    usage: string;
    priorities: string[];
}

// Interface para snapshot do carro
export interface CarSnapshot {
    marca: string;
    modelo: string;
    ano: number;
    preco: number;
    categoria: string;
    combustivel: string;
    cambio: string;
    quilometragem?: number;
}

// Interface para evento de interação
export interface InteractionEvent {
    session_id: string;
    car_id: string;
    interaction_type: InteractionType;
    timestamp: string;
    user_preferences: UserPreferences;
    car_snapshot?: CarSnapshot;
    duration_seconds?: number;
    recommendation_position?: number;
    score?: number;
}

/**
 * Classe para rastrear interações do usuário
 */
class InteractionTracker {
    private sessionId: string;
    private apiBaseUrl: string;
    private enabled: boolean;

    constructor(apiBaseUrl: string = 'http://localhost:8000') {
        this.apiBaseUrl = apiBaseUrl;
        this.sessionId = this.getOrCreateSessionId();
        this.enabled = true; // Pode ser desabilitado via config

        console.log('[InteractionTracker] Inicializado com session_id:', this.sessionId);
    }

    /**
     * Obtém ou cria um session_id único e anônimo
     */
    private getOrCreateSessionId(): string {
        const storageKey = 'faciliauto_session_id';

        // Tentar recuperar do localStorage
        let sessionId = localStorage.getItem(storageKey);

        if (!sessionId) {
            // Criar novo session_id anônimo
            sessionId = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem(storageKey, sessionId);
            console.log('[InteractionTracker] Novo session_id criado:', sessionId);
        }

        return sessionId;
    }

    /**
     * Envia evento para o backend de forma assíncrona
     */
    private async sendEvent(event: InteractionEvent): Promise<void> {
        if (!this.enabled) {
            console.log('[InteractionTracker] Tracking desabilitado');
            return;
        }

        try {
            const response = await axios.post(
                `${this.apiBaseUrl}/api/interactions/track`,
                event,
                {
                    timeout: 5000, // 5 segundos de timeout
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            console.log('[InteractionTracker] Evento enviado:', event.interaction_type, response.data);
        } catch (error) {
            // Não bloquear UI - apenas logar erro
            console.warn('[InteractionTracker] Falha ao enviar evento (não crítico):', error);
        }
    }

    /**
     * Rastreia clique em card de carro
     */
    public async trackCarClick(
        carId: string,
        preferences: UserPreferences,
        carSnapshot?: CarSnapshot,
        position?: number,
        score?: number
    ): Promise<void> {
        const event: InteractionEvent = {
            session_id: this.sessionId,
            car_id: carId,
            interaction_type: 'click',
            timestamp: new Date().toISOString(),
            user_preferences: preferences,
            car_snapshot: carSnapshot,
            recommendation_position: position,
            score: score
        };

        await this.sendEvent(event);
    }

    /**
     * Rastreia visualização de detalhes do carro
     */
    public async trackViewDetails(
        carId: string,
        preferences: UserPreferences,
        carSnapshot?: CarSnapshot,
        position?: number,
        score?: number
    ): Promise<void> {
        const event: InteractionEvent = {
            session_id: this.sessionId,
            car_id: carId,
            interaction_type: 'view_details',
            timestamp: new Date().toISOString(),
            user_preferences: preferences,
            car_snapshot: carSnapshot,
            recommendation_position: position,
            score: score
        };

        await this.sendEvent(event);
    }

    /**
     * Rastreia clique no botão de WhatsApp
     */
    public async trackWhatsAppClick(
        carId: string,
        preferences: UserPreferences,
        carSnapshot?: CarSnapshot,
        position?: number,
        score?: number
    ): Promise<void> {
        const event: InteractionEvent = {
            session_id: this.sessionId,
            car_id: carId,
            interaction_type: 'whatsapp_contact',
            timestamp: new Date().toISOString(),
            user_preferences: preferences,
            car_snapshot: carSnapshot,
            recommendation_position: position,
            score: score
        };

        await this.sendEvent(event);
    }

    /**
     * Rastreia duração de visualização
     */
    public async trackViewDuration(
        carId: string,
        durationSeconds: number,
        preferences: UserPreferences,
        carSnapshot?: CarSnapshot,
        position?: number,
        score?: number
    ): Promise<void> {
        // Só rastrear se visualização for significativa (>= 10 segundos)
        if (durationSeconds < 10) {
            return;
        }

        const event: InteractionEvent = {
            session_id: this.sessionId,
            car_id: carId,
            interaction_type: 'view_details',
            timestamp: new Date().toISOString(),
            user_preferences: preferences,
            car_snapshot: carSnapshot,
            duration_seconds: durationSeconds,
            recommendation_position: position,
            score: score
        };

        await this.sendEvent(event);
    }

    /**
     * Desabilita tracking (para testes ou opt-out)
     */
    public disable(): void {
        this.enabled = false;
        console.log('[InteractionTracker] Tracking desabilitado');
    }

    /**
     * Habilita tracking
     */
    public enable(): void {
        this.enabled = true;
        console.log('[InteractionTracker] Tracking habilitado');
    }

    /**
     * Limpa session_id (útil para testes ou reset)
     */
    public clearSession(): void {
        localStorage.removeItem('faciliauto_session_id');
        this.sessionId = this.getOrCreateSessionId();
        console.log('[InteractionTracker] Session resetada:', this.sessionId);
    }

    /**
     * Retorna o session_id atual
     */
    public getSessionId(): string {
        return this.sessionId;
    }
}

// Exportar instância singleton
const interactionTracker = new InteractionTracker();
export default interactionTracker;
