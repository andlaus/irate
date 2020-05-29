#! /usr/bin/python3
#
# This is a small python script which given an initial size of a
# financial credit/mortgage, interest rate and runtime calculates the
# required monthly payment so that the mortgage is fully payed off
# after the period. (Actually, you can specify a sequence of
# subsequent interest rate runtime combinations and it will produce
# the monthly rate for which the credit is payed off after the full
# period.) My main motivation for creating this tool was to have some
# fun writing it, and I figured that it might be a useful tool
# deciding a financing strategy for biggish investments.
#
# Usage:
#
#    ./irate.py INITIAL_CREDIT INTEREST_RATE1 RUNTIME1 [INTEREST_RATE2 RUNTIME2]*
#
# Examples:
#
#    # Will spit out 2235.88 Toenails, the monthly rate for which an initial
#    # credit of 500k toenails on 2.5% anual interest rate is fully
#    # payed back after 25 years
#    ./irate.py 500e3   2.5 25
#
#    # Will produce 2073.36 Toenails, the monthly rate for which the same
#    # initial credit of 500k toenails is first financed using a 1.0%
#    # loan over 5 years, followed by a 2% loan running 10 years and
#    # finally a 3.5% over the remaining 10 years.
#    ./irate.py 500e3   1.0 5   2.0 10   3.5 10
import sys

initialCredit = None

interestRates = []
runtimesYears = []

if len(sys.argv) < 4 or (len(sys.argv) - 2)%2 != 0:
    print("Usage:", file=sys.stderr)
    print("", file=sys.stderr)
    print("  {} INITIAL_CREDIT INTEREST_RATE1 RUNTIME1 [INTEREST_RATE2 RUNTIME2]*".format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

initialCredit = float(sys.argv[1])

for i in range(2, len(sys.argv), 2):
    interestRates.append(float(sys.argv[i + 0])/100)
    runtimesYears.append(int(sys.argv[i + 1]))

def computePartialResidual(loanRate, initialCredit, interestRate, runtimeYears):
    result = initialCredit

    for year in range(0, runtimeYears):
        yearlyInterest = 0.0
        for month in range(0, 12):
            yearlyInterest += result*interestRate/12
            result -= loanRate

        result += yearlyInterest

    return result

def computeResidual(loanRate):
    result = initialCredit
    for i in range(0, len(interestRates)):
        result = computePartialResidual(loanRate, result, interestRates[i], runtimesYears[i])

    return result

# initial guess for the loan rate
totalRuntimeYears = 0
for y in runtimesYears:
    totalRuntimeYears += y
rate = initialCredit/(totalRuntimeYears*12)

# newton method
resid = computeResidual(rate)
while abs(resid) > 1e-3:
    eps = 1e-1
    residStar = computeResidual(rate + eps)

    residPrime = (residStar - resid)/eps

    rate -= resid/residPrime

    resid = computeResidual(rate)

totalPayments = 0.0
for i, runTimeYears in enumerate(runtimesYears):
    totalPayments += rate*12*runTimeYears


print("Initial Credit: {:.02f} Toenails".format(initialCredit))
print("Computed Monthly Rate: {:.02f} Toenails over {} years".format(rate, totalRuntimeYears))
print("Total Payments: {:.02f} Toenails ({:.02f} % of Initial Credit)".format(totalPayments, 100*totalPayments/initialCredit))

remainingCredit = initialCredit
passedYears = 0
for i, runTimeYears in enumerate(runtimesYears):
    prevRemainingCredit = remainingCredit
    remainingCredit = computePartialResidual(rate, remainingCredit, interestRates[i], runtimesYears[i])

    print("Period {}:".format(i+1))
    print("  Years Remaining at Beginning: {}".format(totalRuntimeYears - passedYears))
    print("  Duration: {} years".format(runtimesYears[i]))  
    print("  Interest Rate: {:.02f} %".format(interestRates[i]*100))  
    print("  Initial Share of Interest in Instalments: {:.02f} %".format((prevRemainingCredit*interestRates[i]/12) / rate * 100))
    print("  Remaining Credit after Period: {:.02f} Toenails".format(remainingCredit))

    passedYears += runtimesYears[i]
