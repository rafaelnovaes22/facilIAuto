#!/usr/bin/env node
/**
 * Smoke tests para validar funcionalidade básica do frontend
 */

import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('\n' + '='.repeat(60));
console.log('SMOKE TESTS - FRONTEND');
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

// Teste 1: Verificar package.json
test('package.json existe', () => {
    const packagePath = join(__dirname, 'package.json');
    if (!existsSync(packagePath)) {
        throw new Error('package.json não encontrado');
    }
    const pkg = JSON.parse(readFileSync(packagePath, 'utf8'));
    if (!pkg.name) throw new Error('package.json inválido');
});

// Teste 2: Verificar dependências principais
test('Dependências principais instaladas', () => {
    const packagePath = join(__dirname, 'package.json');
    const pkg = JSON.parse(readFileSync(packagePath, 'utf8'));

    const required = ['react', 'react-dom', '@chakra-ui/react', 'zustand', 'axios'];
    for (const dep of required) {
        if (!pkg.dependencies[dep]) {
            throw new Error(`Dependência ${dep} não encontrada`);
        }
    }
});

// Teste 3: Verificar estrutura de diretórios
test('Estrutura de diretórios', () => {
    const dirs = [
        'src',
        'src/components',
        'src/pages',
        'src/services',
        'src/store',
        'src/types'
    ];

    for (const dir of dirs) {
        const dirPath = join(__dirname, dir);
        if (!existsSync(dirPath)) {
            throw new Error(`Diretório ${dir} não encontrado`);
        }
    }
});

// Teste 4: Verificar arquivos principais
test('Arquivos principais existem', () => {
    const files = [
        'src/main.tsx',
        'src/App.tsx',
        'src/pages/HomePage.tsx',
        'src/pages/QuestionnairePage.tsx',
        'src/pages/ResultsPage.tsx',
        'src/services/api.ts',
        'src/store/questionnaireStore.ts'
    ];

    for (const file of files) {
        const filePath = join(__dirname, file);
        if (!existsSync(filePath)) {
            throw new Error(`Arquivo ${file} não encontrado`);
        }
    }
});

// Teste 5: Verificar componentes do questionário
test('Componentes do questionário existem', () => {
    const components = [
        'src/components/questionnaire/Step1Budget.tsx',
        'src/components/questionnaire/Step2Usage.tsx',
        'src/components/questionnaire/Step3Priorities.tsx',
        'src/components/questionnaire/Step4Preferences.tsx',
        'src/components/questionnaire/BudgetSlider.tsx',
        'src/components/questionnaire/LocationSelector.tsx',
        'src/components/questionnaire/UsageProfileCard.tsx',
        'src/components/questionnaire/PrioritySlider.tsx'
    ];

    for (const component of components) {
        const componentPath = join(__dirname, component);
        if (!existsSync(componentPath)) {
            throw new Error(`Componente ${component} não encontrado`);
        }
    }
});

// Teste 6: Verificar componentes de resultados
test('Componentes de resultados existem', () => {
    const components = [
        'src/components/results/CarCard.tsx',
        'src/components/results/CarDetailsModal.tsx',
        'src/components/results/ProfileSummary.tsx'
    ];

    for (const component of components) {
        const componentPath = join(__dirname, component);
        if (!existsSync(componentPath)) {
            throw new Error(`Componente ${component} não encontrado`);
        }
    }
});

// Teste 7: Verificar configuração TypeScript
test('TypeScript configurado', () => {
    const tsconfigPath = join(__dirname, 'tsconfig.json');
    if (!existsSync(tsconfigPath)) {
        throw new Error('tsconfig.json não encontrado');
    }
    const tsconfig = JSON.parse(readFileSync(tsconfigPath, 'utf8'));
    if (!tsconfig.compilerOptions) {
        throw new Error('tsconfig.json inválido');
    }
});

// Teste 8: Verificar configuração Vite
test('Vite configurado', () => {
    const vitePath = join(__dirname, 'vite.config.ts');
    if (!existsSync(vitePath)) {
        throw new Error('vite.config.ts não encontrado');
    }
});

// Teste 9: Verificar build TypeScript (sem executar build completo)
test('TypeScript compila sem erros', () => {
    try {
        execSync('npx tsc --noEmit', {
            cwd: __dirname,
            stdio: 'pipe',
            encoding: 'utf8'
        });
    } catch (error) {
        throw new Error('Erros de TypeScript encontrados');
    }
});

console.log('\n' + '='.repeat(60));
console.log(`RESULTADO: ${passed} passou, ${failed} falhou`);
console.log('='.repeat(60) + '\n');

process.exit(failed === 0 ? 0 : 1);
