#include <stdio.h>
#include <generated/hu_cfg.h>

#define ARRAY_SIZE(x) (sizeof(x) / sizeof(*(x)))

/*
 * print check few items from the generated config
 */

static void print_HostUnits(void)
{
	printf("HostUnits: 0x%x\n", HostUnits.hu_en);
	printf("\n");
}

static void print_HostUnit(void)
{
	//for (int i = 0; i < ARRAY_SIZE(HostUnit); i++) {
	for (int i = 0; i < 4; i++) {
		printf("HostUnit[%d].ctl_en: 0x%x\n", i, HostUnit[i].ctl_en);
	}
	printf("\n");
}

void print_HostUnitController(void)
{
	for (int i = 0; i < ARRAY_SIZE((HostUnitController)); i++) {
		for (int j = 0; j < ARRAY_SIZE((HostUnitController[0])); j++) {
			printf("HostUnitController[%d][%d].pf_en: 0x%x\n",
				i, j, HostUnitController[i][j].pf_en);
		}
	}
	printf("\n");
}

void print_HostUnitFunction(void)
{
	for (int i = 0; i < ARRAY_SIZE((HostUnitFunction)); i++) {
		for (int j = 0; j < ARRAY_SIZE((HostUnitFunction[0])); j++) {
			for (int k = 0; k < ARRAY_SIZE((HostUnitFunction[0][0])); k++) {
				int pf_vf = 0;
				printf("HostUnitFunction[%d][%d][%d][%d].nepsq: 0x%x\n",
					i, j, k, pf_vf, HostUnitFunction[i][j][k][pf_vf].nepsq);
					pf_vf = 1;
				printf("HostUnitFunction[%d][%d][%d][%d].nepsq: 0x%x\n",
					i, j, k, pf_vf, HostUnitFunction[i][j][k][pf_vf].nepsq);
			}
		}
	}
	printf("\n");
}

int main(void)
{
	printf("test hu_cfg\n\n");

	print_HostUnits();
	print_HostUnit();
	//print_HostUnitController();
	//print_HostUnitFunction();

	return 0;
}