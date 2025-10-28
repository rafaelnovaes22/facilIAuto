#!/usr/bin/env node
/**
 * Smoke tests simplificados - foca apenas em funcionalidade básica
 */

import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('\n' + '='.repeat(60));
console.log('SMOKE TESTS - FRONTEND (SIMPLIFICADO)');
console.log('='.repeat(60) + '\n');

let passed = 0;
let failed = 0;

function test(name, fn) {
    try {
        fn();
        console.log(`✓ ${name}`);
        passed++;
    } catch (error) {
        console.log(`✗ ${name}: ${error.message}`);
        failed++;
    }
}

// Teste 1: Estrutura de diretórios
test('Estrutura de diretórios', () => {
    const dirs = [
        'src',
        'src/components',
        'src/components/questionnaire',
        'src/components/results',
        'src/pages',
        'src/services',
        'src/store'
    ];

    for (const dir of dirs) {
        if (!existsSync(join(__dirname, dir))) {
            throw new Error(`Diretório ${dir} não encontrado`);
        }
    }
});

// Teste 2: Arquivos principais
test('Arquivos principais existem', () => {
    const files = [
        'src/main.tsx',
        'src/App.tsx',
        'src/pages/HomePage.tsx',
        'src/pages/QuestionnairePage.tsx',
        'src/pages/ResultsPage.tsx'
    ];

    for (const file of files) {
        if (!existsSync(join(__dirname, file))) {
            throw new Error(`Arquivo ${file} não encontrado`);
        }
    }
});

// Teste 3: Componentes do questionário
test('Componentes do questionário', () => {
    const components = [
        'src/components/questionnaire/Step1Budget.tsx',
        'src/components/questionnaire/Step2Usage.tsx',
        'src/components/questionnaire/Step3Priorities.tsx',
        'src/components/questionnaire/Step4Preferences.tsx',
        'src/components/questionnaire/BudgetSlider.tsx',
        'src/components/questionnaire/UsageProfileCard.tsx',
        'src/components/questionnaire/PrioritySlider.tsx'
    ];

    for (const component of components) {
        if (!existsSync(join(__dirname, component))) {
            throw new Error(`Componente ${component} não encontrado`);
        }
    }
});

// Teste 4: Componentes de resultados
test('Componentes de resultados', () => {
    const components = [
        'src/components/results/CarCard.tsx',
        'src/components/results/CarDetailsModal.tsx',
        'src/components/results/ProfileSummary.tsx'
    ];

    for (const component of components) {
        if (!existsSync(join(__dirname, component))) {
            throw new Error(`Componente ${component} não encontrado`);
        }
    }
});

// Teste 5: Serviços e store
test('Serviços e store', () => {
    const files = [
        'src/services/api.ts',
        'src/store/questionnaireStore.ts'
    ];

    for (const file of files) {
        if (!existsSync(join(__dirname, file))) {
            throw new Error(`Arquivo ${file} não encontrado`);
        }
    }
});

// Teste 6: Configurações
test('Arquivos de configuração', () => {
    const configs = [
        'package.json',
        'vite.config.ts',
        'tsconfig.json'
    ];

    for (const config of configs) {
        if (!existsSync(join(__dirname, config))) {
            throw new Error(`Config ${config} não encontrado`);
        }
    }
});

console.log('\n' + '='.repeat(60));
console.log(`RESULTADO: ${passed} passou, ${failed} falhou`);
console.log('='.repeat(60) + '\n');

if (failed === 0) {
    console.log('✓ Todos os smoke tests passaram!');
    console.log('✓ Estrutura do frontend está OK');
    console.log('✓ Todos os componentes principais estão presentes\n');
}

process.exit(failed === 0 ? 0 : 1);
