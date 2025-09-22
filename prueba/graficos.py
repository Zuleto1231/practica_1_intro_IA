import matplotlib.pyplot as plt
import sistemaDifuso

# Gráficos personalizados para funciones de pertenencia
def plot_membership(var, title):
    plt.figure(figsize=(8, 4))
    for label in var.terms:
        plt.plot(var.universe, var[label].mf, label=label, linewidth=2)

    plt.title(f'Funciones de Pertenencia - {title}', fontsize=14)
    plt.xlabel('Valor', fontsize=12)
    plt.ylabel('Pertenencia', fontsize=12)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

retraso, calidad, confiabilidad, simulador_confiabilidad = sistemaDifuso.build_fuzzy_system()

# Visualizar cada variable
plot_membership(calidad, 'Calidad')
plot_membership(retraso, 'Retraso')
plot_membership(confiabilidad, 'Confiabilidad')