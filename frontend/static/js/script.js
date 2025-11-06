document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('purchaseForm');
    const dateInput = document.getElementById('date');
    const billNoInput = document.getElementById('bill_no');
    const clearBtn = document.getElementById('clearBtn');

    const bags = document.getElementById('bags');
    const avgBagWeight = document.getElementById('avg_bag_weight');
    const netWeight = document.getElementById('net_weight');
    const autoNetWeight = document.getElementById('auto_net_weight');
    const rate = document.getElementById('rate');
    const rate150kg = document.getElementById('rate_150kg');
    const useRate150kg = document.getElementById('use_rate_150kg');
    const amount = document.getElementById('amount');
    const bankCommission = document.getElementById('bank_commission');
    const batavPercent = document.getElementById('batav_percent');
    const batav = document.getElementById('batav');
    const shortagePercent = document.getElementById('shortage_percent');
    const shortage = document.getElementById('shortage');
    const autoShortage = document.getElementById('auto_shortage');
    const dalaliRate = document.getElementById('dalali_rate');
    const dalali = document.getElementById('dalali');
    const hammaliRate = document.getElementById('hammali_rate');
    const hammali = document.getElementById('hammali');
    const freight = document.getElementById('freight');
    const rateDiff = document.getElementById('rate_diff');
    const qualityDiff = document.getElementById('quality_diff');
    const moistureDed = document.getElementById('moisture_ded');
    const tds = document.getElementById('tds');
    const totalDeduction = document.getElementById('total_deduction');
    const payableAmount = document.getElementById('payable_amount');
    const paymentAmount = document.getElementById('payment_amount');

    dateInput.valueAsDate = new Date();
    fetchNextBillNo();
    autoNetWeight.checked = true;
    autoShortage.checked = true;

    function fetchNextBillNo() {
        fetch('/api/next-bill-no')
            .then(response => response.json())
            .then(data => {
                billNoInput.value = data.bill_no;
            })
            .catch(error => {
                console.error('Error fetching bill number:', error);
                billNoInput.value = '1';
            });
    }

    function calculateRate150kg() {
        const rate100Val = parseFloat(rate.value) || 0;
        const rate150Val = (rate100Val / 100) * 150;
        rate150kg.value = rate150Val.toFixed(2);
        return rate150Val;
    }

    function calculateFields() {
        const bagsVal = parseFloat(bags.value) || 0;
        const avgBagWeightVal = parseFloat(avgBagWeight.value) || 0;
        const bankCommissionVal = parseFloat(bankCommission.value) || 0;
        const batavPercentVal = parseFloat(batavPercent.value) || 1;
        const shortagePercentVal = parseFloat(shortagePercent.value) || 1;
        const dalaliRateVal = parseFloat(dalaliRate.value) || 10;
        const hammaliRateVal = parseFloat(hammaliRate.value) || 10;
        const freightVal = parseFloat(freight.value) || 0;
        const rateDiffVal = parseFloat(rateDiff.value) || 0;
        const qualityDiffVal = parseFloat(qualityDiff.value) || 0;
        const moistureDedVal = parseFloat(moistureDed.value) || 0;
        const tdsVal = parseFloat(tds.value) || 0;

        let rateVal = parseFloat(rate.value) || 0;
        if (useRate150kg.checked) {
            rateVal = (rateVal / 100) * 150;
        }

        let netWeightVal;
        if (autoNetWeight.checked) {
            netWeightVal = Math.round(bagsVal * avgBagWeightVal * 100) / 100;
            netWeight.value = netWeightVal.toFixed(2);
        } else {
            netWeightVal = parseFloat(netWeight.value) || 0;
            netWeight.removeAttribute('readonly');
        }

        if (autoNetWeight.checked) {
            netWeight.setAttribute('readonly', 'true');
        }

        const amountVal = Math.round(netWeightVal * rateVal * 100) / 100;
        const batavVal = Math.round(amountVal * (batavPercentVal / 100) * 100) / 100;

        let shortageVal;
        if (autoShortage.checked) {
            shortageVal = Math.round(amountVal * (shortagePercentVal / 100) * 100) / 100;
            shortage.setAttribute('readonly', 'true');
        } else {
            shortageVal = parseFloat(shortage.value) || 0;
            shortage.removeAttribute('readonly');
        }

        const dalaliVal = Math.round(netWeightVal * dalaliRateVal * 100) / 100;
        const hammaliVal = Math.round(netWeightVal * hammaliRateVal * 100) / 100;
        const totalDeductionVal = Math.round((bankCommissionVal + batavVal + shortageVal + dalaliVal + hammaliVal + freightVal + rateDiffVal + qualityDiffVal + moistureDedVal + tdsVal) * 100) / 100;
        const payableAmountVal = Math.round((amountVal - totalDeductionVal) * 100) / 100;

        amount.value = amountVal.toFixed(2);
        batav.value = batavVal.toFixed(2);
        if (autoShortage.checked) {
            shortage.value = shortageVal.toFixed(2);
        }
        dalali.value = dalaliVal.toFixed(2);
        hammali.value = hammaliVal.toFixed(2);
        totalDeduction.value = totalDeductionVal.toFixed(2);
        payableAmount.textContent = payableAmountVal.toFixed(2);
        paymentAmount.value = payableAmountVal.toFixed(2);
    }

    rate.addEventListener('input', function() {
        calculateRate150kg();
        calculateFields();
    });

    useRate150kg.addEventListener('change', calculateFields);
    autoNetWeight.addEventListener('change', function() {
        if (this.checked) {
            netWeight.setAttribute('readonly', 'true');
        }
        calculateFields();
    });

    autoShortage.addEventListener('change', function() {
        if (this.checked) {
            shortage.setAttribute('readonly', 'true');
        }
        calculateFields();
    });

    shortage.addEventListener('input', function() {
        if (!autoShortage.checked) {
            calculateFields();
        }
    });

    document.querySelectorAll('.calc-input').forEach(input => {
        input.addEventListener('input', calculateFields);
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            data[key] = value;
        });

        data['net_weight'] = netWeight.value;
        data['amount'] = amount.value;
        data['batav'] = batav.value;
        data['shortage'] = shortage.value;
        data['dalali'] = dalali.value;
        data['hammali'] = hammali.value;
        data['freight'] = freight.value;
        data['rate_diff'] = rateDiff.value;
        data['quality_diff'] = qualityDiff.value;
        data['moisture_ded'] = moistureDed.value;
        data['tds'] = tds.value;
        data['total_deduction'] = totalDeduction.value;
        data['payable_amount'] = payableAmount.textContent;

        try {
            const response = await fetch('/api/add-slip', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                alert('Purchase slip saved successfully!');
                window.open(`/print/${result.slip_id}`, '_blank');
                form.reset();
                dateInput.valueAsDate = new Date();
                fetchNextBillNo();
                autoNetWeight.checked = true;
                autoShortage.checked = true;
                calculateFields();
            } else {
                alert('Error saving slip: ' + result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving purchase slip');
        }
    });

    clearBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the form?')) {
            form.reset();
            dateInput.valueAsDate = new Date();
            fetchNextBillNo();
            autoNetWeight.checked = true;
            autoShortage.checked = true;
            calculateFields();
        }
    });

    calculateRate150kg();
    calculateFields();
});
