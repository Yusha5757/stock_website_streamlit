import os
import requests
import streamlit as st
from datetime import date
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from darts import TimeSeries
from darts.models import ExponentialSmoothing
import numpy as np
from datetime import datetime, timedelta


# Constants
START = "2015-01-01"
TODAY = pd.Timestamp(date.today())

# Initialize session state variables
if 'last_question' not in st.session_state:
    st.session_state.last_question = ""
    st.session_state.last_answer = ""

# Define question-answer pairs and keywords for the chatbot
qa_pairs = {
    "What is a good investment strategy?": "Consider diversifying your portfolio and investing for the long term.",
    "How do I buy stocks?": "You can buy stocks through a brokerage account.",
    "What is the stock market?": "The stock market is a collection of markets where stocks are traded.",
    "What does ETF mean?": "ETF stands for Exchange-Traded Fund, a type of investment fund.",
    "What is a credit score?": "A numerical representation of an individual's creditworthiness based on credit history and payment behavior.",
    "What is diversification in investing?": "Diversification is an investment strategy that involves spreading investments across various assets, sectors, or geographical areas to reduce overall risk. By not concentrating investments in one area, an investor can protect themselves against significant losses if a single investment performs poorly. A well-diversified portfolio can help achieve more stable returns over time, especially in volatile markets.",



    "What is a stock option?": "A stock option is a financial derivative that gives an investor the right, but not the obligation, to buy or sell a stock at a predetermined price within a specific timeframe. Stock options are often used as incentives in employee compensation packages, allowing employees to purchase company stock at a discount, potentially leading to significant financial gains if the company's stock price increases.",

    "What is market capitalization?": "Market capitalization, or market cap, is the total market value of a company's outstanding shares of stock, calculated by multiplying the current share price by the total number of shares. It is used as a measure of a company's size and can indicate its growth potential. Companies are often classified as large-cap, mid-cap, or small-cap based on their market capitalization, which can influence investment strategies.",

    "What is the difference between growth and value investing?": "Growth investing focuses on companies expected to grow at an above-average rate compared to their industry or the market. Investors seek stocks with strong potential for price appreciation, often willing to pay higher valuations. Value investing, on the other hand, involves finding undervalued stocks that are trading for less than their intrinsic value. Value investors look for bargains, believing that the market will eventually correct the price.",

    "What is a stock split?": "A stock split occurs when a company divides its existing shares into multiple new shares to increase liquidity. For example, in a 2-for-1 split, each shareholder receives an additional share for every share they own, effectively halving the stock price. While the overall value of the company remains unchanged, a stock split can make shares more affordable for a broader range of investors, potentially increasing demand.",

    "What is a margin account?": "A margin account allows investors to borrow money from a broker to purchase securities, using their existing investments as collateral. This can amplify returns but also increases risk, as losses can be magnified. Investors must maintain a minimum balance, known as the maintenance margin, and if the account falls below this threshold, the broker may issue a margin call, requiring additional funds to be deposited.",

    "What are ETFs?": "Exchange-traded funds (ETFs) are investment funds that trade on stock exchanges, similar to individual stocks. They typically track an index, commodity, or a basket of assets and offer investors a way to diversify their portfolios at a lower cost than mutual funds. ETFs can be bought and sold throughout the trading day, providing flexibility and ease of access for investors.",

    "What is a bull market?": "A bull market refers to a financial market condition characterized by rising prices of securities, typically by 20% or more from recent lows. Bull markets can occur in any asset class, including stocks, bonds, or commodities, and are often driven by strong economic indicators, investor confidence, and favorable market conditions. Investors are generally more optimistic during bull markets, leading to increased buying activity.",

    "What is a liquidity ratio?": "A liquidity ratio measures a company's ability to cover its short-term obligations with its short-term assets. Common liquidity ratios include the current ratio and quick ratio. A higher liquidity ratio indicates better financial health, as it suggests that the company has sufficient assets to cover its liabilities, which is crucial for maintaining operations and avoiding financial distress.",

    "What is behavioral finance?": "Behavioral finance is a field that studies the psychological influences on investors and financial markets. It examines how cognitive biases, emotions, and social factors can affect investment decisions and market outcomes. Understanding behavioral finance can help investors recognize and mitigate biases that may lead to irrational decision-making, ultimately leading to better investment performance.",

    "What is a 529 plan?": "A 529 plan is a tax-advantaged savings plan designed to encourage saving for future education costs. The plans are sponsored by states, state agencies, or educational institutions, and the funds can be used for qualified expenses, including tuition, fees, and room and board. Contributions grow tax-free, and withdrawals for educational purposes are also tax-free, making 529 plans an effective tool for education funding.",

    "What is a financial advisor?": "A financial advisor is a professional who provides financial planning and investment advice to clients. They help individuals and organizations develop strategies to manage their finances, including budgeting, retirement planning, investment management, and tax strategies. Financial advisors may charge fees based on assets under management, hourly rates, or flat fees, depending on their business model.",

    "What is a cash reserve?": "A cash reserve is a portion of liquid assets set aside for emergencies or unexpected expenses. Maintaining a cash reserve is crucial for financial stability, as it provides a safety net that can cover living expenses during unforeseen circumstances, such as job loss or medical emergencies. Financial experts often recommend having enough cash reserves to cover three to six months of living expenses.",

    "What is the difference between an asset and a liability?": "An asset is a resource owned by an individual or company that has economic value and can provide future benefits, such as cash, real estate, or investments. A liability, on the other hand, is a financial obligation or debt that an individual or company owes to another party. Understanding the balance between assets and liabilities is key to assessing financial health and net worth.",

    "What is a bull spread?": "A bull spread is an options trading strategy used when an investor expects a moderate increase in the price of an underlying asset. It involves buying a call option at a lower strike price while simultaneously selling another call option at a higher strike price. This strategy limits both potential profit and loss, making it a more conservative approach than simply buying a call option.",

    "What is a financial portfolio?": "A financial portfolio is a collection of financial assets such as stocks, bonds, mutual funds, real estate, and cash equivalents held by an individual or institution. The goal of a portfolio is to maximize returns while managing risk through diversification. Portfolio management involves regularly reviewing and adjusting investments to align with financial goals and market conditions.",

    "What is asset allocation?": "Asset allocation is the process of distributing investments among different asset classes, such as stocks, bonds, and cash, to optimize risk and return based on individual goals and risk tolerance. A well-balanced asset allocation strategy helps mitigate risk by diversifying investments, ensuring that poor performance in one area doesn’t significantly impact overall returns.",

    "What is a credit default swap?": "A credit default swap (CDS) is a financial derivative that allows an investor to 'swap' or transfer the credit risk of a borrower to another party. The buyer of a CDS makes periodic payments to the seller, who agrees to compensate the buyer in the event of a default on the underlying loan or bond. CDSs are often used by investors to hedge against credit risk or speculate on changes in credit quality.",

    "What is a tax-deferred account?": "A tax-deferred account is a type of investment account where taxes on earnings, such as interest, dividends, and capital gains, are postponed until withdrawals are made. Common examples include traditional IRAs and 401(k) plans. This feature allows investments to grow without immediate tax implications, enabling individuals to accumulate wealth more efficiently for retirement.",

    "What is a brokerage account?": "A brokerage account is an investment account that allows individuals to buy and sell various securities, such as stocks, bonds, and mutual funds, through a licensed brokerage firm. Brokerage accounts can be taxable or tax-advantaged, and they provide investors with access to financial markets. Investors can choose between full-service brokers, who offer personalized advice, or discount brokers, who charge lower fees but offer less guidance.",

    "What is a financial market?": "A financial market is a marketplace where buyers and sellers come together to trade financial assets, such as stocks, bonds, currencies, and derivatives. These markets play a crucial role in the economy by facilitating capital allocation, price discovery, and risk management. Major financial markets include stock exchanges, bond markets, and foreign exchange markets.",

    "What is a limit order?": "A limit order is an order to buy or sell a security at a specific price or better. For buyers, this means purchasing at or below the limit price; for sellers, it means selling at or above the limit price. Limit orders provide control over the price at which a trade is executed, but there is no guarantee that the order will be filled, especially if the market price does not reach the specified limit.",

    "What is an IPO?": "An initial public offering (IPO) is the process through which a private company offers its shares to the public for the first time. This process allows the company to raise capital from public investors and transition into a publicly traded company. IPOs are often seen as significant milestones for companies and can generate substantial media attention and investor interest.",

    "What is a non-fungible token (NFT)?": "A non-fungible token (NFT) is a unique digital asset that represents ownership of a specific item or piece of content on a blockchain, typically Ethereum. Unlike cryptocurrencies, which are fungible and can be exchanged for one another, NFTs are unique and cannot be replaced. NFTs have gained popularity in the art world, gaming, and collectibles, allowing creators to monetize their digital works.",

    "What is a bear market?": "A bear market is a financial market condition characterized by a prolonged period of declining prices, typically defined as a drop of 20% or more from recent highs. Bear markets can occur in various asset classes and are often associated with economic downturns or negative investor sentiment. Investors may adopt more conservative strategies during bear markets to mitigate losses.",

    "What is quantitative easing?": "Quantitative easing (QE) is a monetary policy used by central banks to stimulate the economy by increasing the money supply. This is typically done by purchasing government securities or other financial assets, which lowers interest rates and encourages lending and investment. QE aims to boost economic activity during periods of low inflation and economic stagnation.",

    "What is a trading strategy?": "A trading strategy is a plan or set of rules that traders use to determine when to enter or exit trades. Strategies can be based on various factors, including technical analysis, fundamental analysis, or market trends. Successful trading strategies are often backed by research and tested through historical data to identify potential profitability.",

    "What is peer-to-peer lending?": "Peer-to-peer lending (P2P) is a method of borrowing and lending money directly between individuals without the involvement of traditional financial institutions. Online platforms connect borrowers seeking loans with investors willing to fund them, often resulting in lower interest rates for borrowers and higher returns for investors. P2P lending has gained popularity as an alternative to conventional lending methods.",

    "What is a hedge fund?": "A hedge fund is an investment vehicle that pools capital from accredited investors and employs various strategies to generate high returns. Hedge funds may invest in a wide range of assets, including stocks, bonds, commodities, and derivatives, often using leverage and short selling. Due to their complex structures and strategies, hedge funds are typically less regulated than mutual funds and may have higher fees.",

    "What is an annuity?": "An annuity is a financial product that provides a series of payments made at equal intervals. Annuities are often used as a source of retirement income, with individuals paying a lump sum or series of payments in exchange for guaranteed future payouts. Annuities can be fixed or variable, depending on whether the payments are predetermined or fluctuate based on investment performance.",

    "What is a tax credit?": "A tax credit is a dollar-for-dollar reduction in a taxpayer's liability to the government. Unlike deductions, which reduce taxable income, tax credits directly lower the amount of tax owed. Tax credits can be nonrefundable, meaning they can reduce tax liability to zero but not beyond, or refundable, which allows taxpayers to receive a refund if the credit exceeds their tax liability.",

    "What is financial literacy?": "Financial literacy refers to the understanding of financial concepts and the ability to make informed financial decisions. It includes knowledge of budgeting, investing, debt management, and understanding financial products. Increasing financial literacy is crucial for individuals to effectively manage their finances, plan for the future, and avoid common pitfalls such as excessive debt or poor investment choices.",

    "What is inflation?": "Inflation is the rate at which the general level of prices for goods and services rises, eroding purchasing power. It is typically measured by the Consumer Price Index (CPI) or the Producer Price Index (PPI). Moderate inflation is considered a sign of a growing economy, but high inflation can lead to uncertainty and decreased consumer spending, affecting economic stability.",

    "What is a credit card?": "A credit card is a payment card that allows the cardholder to borrow funds from a pre-approved credit limit to make purchases or withdraw cash. Credit cards typically come with interest rates, fees, and rewards programs, making them a popular choice for convenient transactions. Responsible use of credit cards can help build a positive credit history, while mismanagement can lead to debt accumulation.",

    "What is a bear spread?": "A bear spread is an options trading strategy employed when an investor expects a moderate decline in the price of an underlying asset. It involves buying a put option at a higher strike price and simultaneously selling another put option at a lower strike price. This strategy limits both potential gains and losses, making it a conservative approach to bearish market sentiment.",

    "What is a cash flow statement?": "A cash flow statement is a financial document that provides a summary of cash inflows and outflows over a specific period. It helps stakeholders understand how a company generates cash from operations, investing, and financing activities. Analyzing cash flow statements is crucial for assessing liquidity and overall financial health, as it shows how well a company can meet its obligations.",

    "What is a credit score?": "A credit score is a numerical representation of an individual's creditworthiness, typically ranging from 300 to 850. It is calculated based on credit history, including payment history, credit utilization, length of credit history, types of credit accounts, and recent inquiries. Higher credit scores generally lead to better loan terms, lower interest rates, and increased chances of credit approval.",

    "What is a sell-off?": "A sell-off is a rapid decline in the price of an asset, often triggered by negative news, economic downturns, or shifts in investor sentiment. During a sell-off, investors may panic and rush to sell their holdings, exacerbating the decline. While sell-offs can present buying opportunities for some investors, they can also signal underlying issues within the market or economy.",

    "What is dollar-cost averaging?": "Dollar-cost averaging is an investment strategy that involves regularly investing a fixed amount of money into a particular asset or portfolio, regardless of its price. This approach helps reduce the impact of volatility and minimizes the risk of making poor investment decisions based on market timing. Over time, dollar-cost averaging can lead to a lower average purchase price and increased long-term returns.",

    "What is a mutual fund's expense ratio?": "The expense ratio of a mutual fund represents the annual fees expressed as a percentage of the fund's assets. These fees cover management, administration, and other operational costs. A lower expense ratio is generally preferable, as high fees can erode investment returns over time. Investors should consider the expense ratio alongside performance metrics when evaluating mutual funds.",

    "What is a stock buyback?": "A stock buyback, or share repurchase, occurs when a company buys back its own shares from the marketplace. This can reduce the number of outstanding shares, potentially increasing earnings per share (EPS) and enhancing shareholder value. Companies may initiate buybacks as a way to return excess cash to shareholders, signal confidence in the business, or improve financial ratios.",

    "What is a stock market index?": "A stock market index is a statistical measure that tracks the performance of a specific group of stocks, representing a segment of the stock market. Common indices include the S&P 500, Dow Jones Industrial Average, and Nasdaq Composite. Indices provide investors with insights into market trends and can serve as benchmarks for portfolio performance.",

    "What is a performance bond?": "A performance bond is a type of surety bond that guarantees the satisfactory completion of a project or contract. If the contractor fails to fulfill the obligations, the bond issuer compensates the project owner. Performance bonds are often used in construction and other industries to provide financial security and ensure that projects are completed as specified.",

    "What is an option contract?": "An option contract is a financial agreement that gives the buyer the right, but not the obligation, to buy or sell an underlying asset at a specified price before a certain date. Options can be used for hedging, speculation, or increasing leverage in an investment portfolio. They come in two types: call options (the right to buy) and put options (the right to sell).",

    "What is a credit line?": "A credit line, or line of credit, is a flexible loan option that allows borrowers to access funds up to a specified limit. Borrowers can draw on the credit line as needed, paying interest only on the amount used. Lines of credit are commonly used for personal or business expenses, providing a safety net for cash flow fluctuations or emergencies.",

    "What is a personal loan?": "A personal loan is an unsecured loan issued to individuals for various purposes, such as consolidating debt, financing large purchases, or covering unexpected expenses. Personal loans typically have fixed interest rates and repayment terms, making them a straightforward borrowing option. Borrowers should compare rates and terms from multiple lenders to secure the best deal.",

    "What is a buy-and-hold strategy?": "A buy-and-hold strategy is an investment approach that involves purchasing securities and holding them for an extended period, regardless of market fluctuations. This strategy is based on the belief that, over time, the market will rise, allowing investors to benefit from long-term capital appreciation. Buy-and-hold investors often focus on fundamental analysis and ignore short-term market noise.",

    "What is a variable annuity?": "A variable annuity is a type of annuity contract that allows investors to allocate their premiums among various investment options, such as mutual funds. The payouts from variable annuities can fluctuate based on the performance of the chosen investments, providing the potential for higher returns compared to fixed annuities. However, they also come with more risk and fees.",

    "What is a savings account?": "A savings account is a deposit account held at a financial institution that pays interest on the deposited funds. Savings accounts provide a safe and accessible place for individuals to store money while earning a modest return. They are typically used for short-term savings goals, emergencies, or as a place to hold funds before making investments.",

    "What is a financial analyst?": "A financial analyst is a professional who analyzes financial data to help businesses and individuals make informed investment decisions. Analysts assess the performance of stocks, bonds, and other securities, often using quantitative and qualitative methods. They may work for investment firms, banks, or corporations, providing insights and recommendations based on their analyses.",

    "What is a recession?": "A recession is a significant decline in economic activity across the economy that lasts for an extended period, typically recognized as two consecutive quarters of negative GDP growth. During a recession, businesses may experience reduced demand, leading to layoffs, lower consumer spending, and decreased investment. Governments and central banks often respond with stimulus measures to stimulate growth.",

    "What is a stock market crash?": "A stock market crash is a sudden and significant decline in stock prices, often triggered by economic factors, geopolitical events, or market speculation. Crashes can lead to panic selling and loss of investor confidence, resulting in widespread financial instability. They are typically characterized by a rapid drop in major stock indices and can have long-lasting effects on the economy.",

    "What is a hedge?": "In finance, a hedge is an investment strategy used to offset potential losses in another investment by taking an opposing position. Hedging can be achieved through various instruments, such as options, futures, or diversifying assets. While hedging can reduce risk, it may also limit potential gains, making it essential for investors to weigh the benefits and drawbacks.",

    "What is a fiscal policy?": "Fiscal policy refers to the government's use of spending and taxation to influence the economy. By adjusting tax rates and government spending, policymakers aim to promote economic growth, reduce unemployment, and stabilize prices. Expansionary fiscal policy involves increasing spending or cutting taxes to stimulate growth, while contractionary fiscal policy focuses on reducing spending or increasing taxes to curb inflation.",

    "What is a venture capital?": "Venture capital is a form of private equity financing that provides funding to early-stage, high-potential startups in exchange for equity ownership. Venture capitalists typically seek to invest in innovative companies with significant growth potential, helping them scale and succeed. In return for their investment, venture capitalists often take an active role in guiding the company's strategy and operations.",

    "What is a debt-to-equity ratio?": "The debt-to-equity ratio is a financial metric that compares a company's total liabilities to its shareholders' equity. It is used to assess a company's financial leverage and risk. A high debt-to-equity ratio may indicate greater risk, as the company relies more on borrowed funds, while a lower ratio suggests a more conservative capital structure with less reliance on debt financing.",

    "What is a limit price?": "A limit price is the specified price at which a trader intends to buy or sell a security through a limit order. For a buy limit order, the trader sets the maximum price they are willing to pay, while for a sell limit order, they specify the minimum price at which they are willing to sell. Limit prices allow traders to control execution prices, although there is no guarantee that the order will be filled.",

    "What is a market order?": "A market order is an order to buy or sell a security immediately at the current market price. Unlike limit orders, which specify a price, market orders prioritize speed of execution, making them suitable for traders looking to quickly enter or exit positions. However, market orders can be subject to price fluctuations, particularly in volatile markets.",

    "What is insider trading?": "Insider trading refers to the buying or selling of a publicly-traded company's stock based on non-public, material information about the company. While not all insider trading is illegal, trading based on confidential information violates securities laws and can result in severe penalties. Regulatory agencies monitor and investigate insider trading to maintain market integrity.",

    "What is a convertible bond?": "A convertible bond is a type of bond that can be converted into a predetermined number of shares of the issuing company’s stock at specified times during its life. This hybrid security offers investors the opportunity to benefit from both fixed income and equity potential, allowing them to convert their bonds into stock if the company performs well, thus maximizing potential returns.",

    "What is a stock exchange?": "A stock exchange is a regulated marketplace where securities, such as stocks and bonds, are bought and sold. Major stock exchanges, like the New York Stock Exchange (NYSE) and Nasdaq, provide a platform for companies to raise capital through public offerings and for investors to trade securities. Exchanges play a crucial role in price discovery and maintaining liquidity in the financial markets.",

    "What is economic indicators?": "Economic indicators are statistics that provide insights into the health and performance of an economy. Common indicators include GDP growth, unemployment rates, inflation rates, and consumer confidence. These indicators help policymakers, investors, and businesses make informed decisions, as they reflect current economic conditions and can forecast future trends.",

    "What is a return on investment (ROI)?": "Return on investment (ROI) is a financial metric used to evaluate the profitability of an investment relative to its cost. It is calculated by dividing the net profit from the investment by the initial cost and expressing it as a percentage. A higher ROI indicates a more favorable investment outcome, helping investors assess the efficiency of their capital allocation.",

    "What is a collateralized loan?": "A collateralized loan is a loan that is secured by an asset, which serves as collateral for the lender. If the borrower defaults, the lender has the right to seize the collateral to recover their losses. Collateralized loans typically have lower interest rates than unsecured loans, as they pose less risk to lenders. Common types of collateral include real estate, vehicles, or savings accounts.",

    "What is a sovereign bond?": "A sovereign bond is a debt security issued by a national government to finance government spending and obligations. Sovereign bonds are generally considered low-risk investments, as they are backed by the full faith and credit of the issuing government. However, the risk level can vary depending on the country's economic stability and credit rating.",

    "What is a financial bubble?": "A financial bubble is a market phenomenon characterized by rapidly rising asset prices that exceed their intrinsic value, often driven by exuberant investor behavior. Bubbles can occur in various markets, including real estate, stocks, and cryptocurrencies. When the bubble bursts, it typically results in a sharp decline in prices, leading to significant losses for investors.",

    "What is a fixed-rate mortgage?": "A fixed-rate mortgage is a type of home loan with an interest rate that remains constant throughout the life of the loan. This provides predictability in monthly payments, making it easier for borrowers to budget. Fixed-rate mortgages are popular for long-term financing, as they protect borrowers from interest rate fluctuations that can occur with adjustable-rate mortgages.",

    "What is a financial statement?": "A financial statement is a formal record of the financial activities of a business, organization, or individual. Common types include the balance sheet, income statement, and cash flow statement. Financial statements provide insights into the entity's financial health, performance, and cash flow, helping stakeholders make informed decisions regarding investments, credit, and management.",

    "What is a central bank?": "A central bank is a financial institution that manages a country’s currency, money supply, and interest rates. Central banks are responsible for implementing monetary policy, regulating financial institutions, and providing financial services to the government. Their primary goals often include maintaining price stability, controlling inflation, and supporting economic growth.",

    "What is a market risk?": "Market risk is the potential for losses due to fluctuations in the market value of an investment. This risk arises from changes in factors such as interest rates, currency exchange rates, and economic conditions. Investors can mitigate market risk through diversification and hedging strategies, but it is an inherent part of investing in financial markets.",

    "What is a tax-deferred growth?": "Tax-deferred growth refers to the increase in the value of investments that are not subject to taxes until a later date. This concept is common in retirement accounts like 401(k)s and IRAs, allowing investments to compound without the immediate tax burden. Tax-deferred growth can significantly enhance long-term investment returns, making it an appealing feature for retirement planning.",

    "What is a real estate bubble?": "A real estate bubble occurs when property prices rise rapidly to levels that are unsustainable, driven by speculation, demand, and easy access to credit. When the bubble bursts, prices can plummet, leading to significant losses for homeowners and investors. Understanding the signs of a real estate bubble is crucial for making informed investment decisions in the property market.",

    "What is a certificate of deposit (CD)?": "A certificate of deposit (CD) is a time deposit offered by banks and credit unions that pays interest at a fixed rate for a specified period. CDs are considered low-risk investments, as they provide guaranteed returns and are often insured by the FDIC up to certain limits. Investors typically receive their principal plus interest at maturity, but early withdrawals may incur penalties.",
    "What is an index fund?": "An index fund is a type of mutual fund or ETF that aims to replicate the performance of a specific index, such as the S&P 500. By investing in an index fund, investors gain exposure to a broad market segment, as these funds typically hold all or a representative sample of the securities in the index. This passive management strategy often results in lower fees compared to actively managed funds, making index funds an attractive option for cost-conscious investors.",

    "What is financial literacy?": "Financial literacy is the ability to understand and effectively use various financial skills, including personal finance management, budgeting, investing, and understanding credit. It empowers individuals to make informed decisions about their finances, helping them to plan for the future, avoid debt, and grow their wealth. Increasing financial literacy is crucial for navigating today's complex financial landscape.",

    "What is compound interest?": "Compound interest is the interest calculated on the initial principal as well as on the accumulated interest from previous periods. This effect can significantly increase the amount of interest earned over time, making it a powerful concept in investing and savings. For example, if you invest $1,000 at an annual interest rate of 5%, compounded annually, after 30 years, you would have accumulated approximately $4,321, demonstrating the impact of compounding.",

    "What are bonds?": "Bonds are fixed-income securities that represent a loan made by an investor to a borrower, typically a corporation or government. In exchange for the loan, the borrower pays periodic interest to the bondholder and returns the principal amount at maturity. Bonds are considered less risky than stocks and can provide a steady income stream, making them popular among conservative investors seeking stability in their portfolios.",

    "What is a bear market?": "A bear market is defined as a period during which stock prices fall by 20% or more from recent highs. It reflects widespread investor pessimism and can occur due to economic downturns or geopolitical crises. Bear markets can lead to significant declines in asset values and can impact investor sentiment for extended periods.",

    "What is a stock market correction?": "A stock market correction is a decline of 10% or more in the price of a stock or market index from its recent peak. Corrections are often viewed as a natural part of the market cycle, helping to prevent bubbles by allowing overvalued assets to adjust to more sustainable levels. While they can induce fear among investors, corrections can also present buying opportunities for those looking to enter the market.",

    "What is a risk-adjusted return?": "A risk-adjusted return measures the return of an investment relative to the risk taken to achieve that return. It allows investors to compare the performance of different investments on a level playing field by accounting for the volatility and potential losses associated with each option. Common metrics for evaluating risk-adjusted returns include the Sharpe ratio and the Treynor ratio, which help investors make informed choices based on their risk tolerance.",

    "What is a stock buyback?": "A stock buyback, or share repurchase, occurs when a company buys back its own shares from the market. This reduces the number of outstanding shares, which can increase earnings per share and potentially raise the stock price. Companies may initiate buybacks to return capital to shareholders, signal confidence in their financial health, or utilize excess cash effectively. However, it can also lead to concerns if it appears the company is prioritizing short-term stock performance over long-term growth.",

    "What is the difference between primary and secondary markets?": "The primary market is where new securities are issued and sold for the first time, typically through initial public offerings (IPOs). Investors purchase directly from the issuer. The secondary market, on the other hand, involves the buying and selling of existing securities among investors. Prices in the secondary market fluctuate based on supply and demand, reflecting the ongoing valuation of the assets after their initial sale.",

    "What is a financial statement?": "A financial statement is a formal record of the financial activities and position of a business, organization, or individual. The three main types are the income statement, balance sheet, and cash flow statement. Together, these documents provide a comprehensive view of a company's financial health, performance, and cash management, helping investors make informed decisions about potential investments.",

    "What is diversification?": "Diversification is an investment strategy that involves spreading investments across various financial instruments, industries, and other categories to reduce risk. By not putting all your eggs in one basket, you can mitigate the impact of poor performance in any single asset or sector. This approach is vital for building a balanced portfolio that can weather market volatility.",

    "What is a liquidity event?": "A liquidity event is an occurrence that allows investors to convert their equity investments into cash. This typically happens through avenues like initial public offerings (IPOs), mergers, or acquisitions. Liquidity events are significant milestones for investors as they provide a return on investment and often lead to substantial financial gain.",

    "What is a hedge fund?": "A hedge fund is a pooled investment fund that employs various strategies to earn high returns for its investors. These strategies may include leveraging, short selling, and derivatives trading. Unlike mutual funds, hedge funds are typically open to a limited range of investors and may require higher minimum investments, as well as carry higher fees due to active management.",

    "What is a credit score?": "A credit score is a numerical representation of an individual's creditworthiness, calculated based on credit history, payment behavior, and outstanding debts. Lenders use credit scores to assess the risk of lending money or extending credit to borrowers. Higher scores indicate lower risk, while lower scores can result in higher interest rates or difficulty obtaining credit.",

    "What are retirement accounts?": "Retirement accounts are specialized savings accounts designed to encourage individuals to save for retirement while offering tax advantages. Common types include 401(k) plans, IRAs, and Roth IRAs. These accounts often have contribution limits and tax implications that vary based on the account type, but they generally provide tax-deferred growth or tax-free withdrawals in retirement.",

    "What is passive income?": "Passive income refers to earnings derived from ventures in which a person is not actively involved, allowing for income generation with minimal effort. Common sources include rental income, dividends from investments, and earnings from a business in which one does not actively participate. Building streams of passive income can enhance financial freedom and stability.",

    "What is a balance sheet?": "A balance sheet is a financial statement that provides a snapshot of a company's assets, liabilities, and equity at a specific point in time. It follows the accounting equation: Assets = Liabilities + Equity. Analyzing the balance sheet helps stakeholders assess a company's financial health, liquidity, and overall stability, guiding investment decisions.",

    "What is a cash flow statement?": "A cash flow statement is a financial report that outlines the inflows and outflows of cash within a company over a specific period. It categorizes cash flows into operating, investing, and financing activities. Understanding cash flow is crucial for assessing a company's liquidity, operational efficiency, and ability to fund growth or pay debts.",

    "What is an annuity?": "An annuity is a financial product that provides a series of payments made at equal intervals, typically used for retirement income. Annuities can be structured as immediate or deferred, and they may be fixed or variable. They offer the advantage of providing a steady income stream, but it's essential to understand their terms, fees, and tax implications before investing.",

    "What is capital gains tax?": "Capital gains tax is the tax levied on the profit earned from the sale of an asset, such as stocks or real estate. The tax rate can differ based on how long the asset was held: short-term capital gains (assets held for less than a year) are typically taxed at ordinary income rates, while long-term gains benefit from lower tax rates. Understanding capital gains tax is essential for effective tax planning.",

    "What is a tax deduction?": "A tax deduction is an expense that reduces taxable income, thereby lowering the amount of tax owed to the government. Common deductions include mortgage interest, student loan interest, and certain business expenses. Taking advantage of available deductions can lead to significant tax savings and improve overall financial health.",

    "What is a tax credit?": "A tax credit directly reduces the amount of tax owed, providing a dollar-for-dollar reduction in tax liability. Unlike deductions, which lower taxable income, credits offer a more immediate benefit. Tax credits can be available for various reasons, such as education expenses, energy-efficient home improvements, or low-income housing investments.",

     "What is stock price?": "The stock price is the current price at which a stock is being bought or sold on the stock market. It reflects the market's perception of a company's value, influenced by various factors including supply and demand, economic conditions, and investor sentiment. A rising stock price typically signals investor confidence, while a declining price may indicate uncertainty.",

    "What affects stock prices?": "Stock prices are influenced by company performance, market conditions, investor sentiment, and economic indicators. Factors like earnings reports, news about management, and macroeconomic changes can lead to fluctuations. Additionally, market trends, interest rates, and geopolitical events play significant roles in driving stock prices up or down.",

    "What is a moving average?": "A moving average is a statistical tool used to smooth out price data by creating averages over specific periods. It helps identify trends by reducing short-term fluctuations. For instance, a 50-day moving average takes the average price over the last 50 days, helping traders discern whether a stock is in an upward or downward trend.",

    "What is a bullish market?": "A bullish market, or bull market, is characterized by rising stock prices and investor optimism. This phase often coincides with economic growth, low unemployment, and high consumer confidence. Investors tend to buy stocks, expecting prices to continue rising, creating a positive feedback loop that further boosts the market.",

    "What are dividends?": "Dividends are distributions of a company's earnings to its shareholders, typically paid out in cash or additional shares. They provide a way for companies to share profits and reward investors. Regular dividends can signal financial health and stability, making dividend-paying stocks attractive to income-seeking investors.",

    "What is market capitalization?": "Market capitalization is the total market value of a company's outstanding shares, calculated by multiplying the stock price by the number of shares. It serves as a measure of a company's size and stability, often categorizing firms into small-cap, mid-cap, and large-cap segments, which have different risk and growth profiles.",

    "What is the S&P 500?": "The S&P 500 is a stock market index that tracks the performance of 500 of the largest publicly traded companies in the U.S. It serves as a benchmark for the overall U.S. stock market, providing insights into economic trends. Investors often use the S&P 500 to gauge market performance and compare their portfolios.",

    "What is a bear market?": "A bear market is defined as a period during which stock prices fall by 20% or more from recent highs. It reflects widespread investor pessimism and can occur due to economic downturns or geopolitical crises. Bear markets can lead to significant declines in asset values and can impact investor sentiment for extended periods.",

    "What are ETFs?": "Exchange-Traded Funds (ETFs) are investment funds that trade on stock exchanges, similar to individual stocks. They typically hold a diversified portfolio of assets, providing investors with exposure to various markets or sectors. ETFs offer the advantages of diversification, lower fees, and flexibility in trading.",

    "What is a stock split?": "A stock split occurs when a company divides its existing shares into multiple new shares, increasing the number of shares outstanding while reducing the price per share. For example, in a 2-for-1 split, each shareholder receives an additional share for each share owned. Stock splits can enhance liquidity and make shares more affordable to a broader range of investors.",

    "How do I buy stocks?": "To buy stocks, you need to open a brokerage account, deposit funds, and select stocks to purchase. You can use online trading platforms to place orders. A market order buys shares at the current price, while a limit order allows you to specify the maximum price you're willing to pay. Researching stocks beforehand is crucial for informed decision-making.",

    "What is an IPO?": "An Initial Public Offering (IPO) is the first sale of stock by a private company to the public, allowing it to raise capital. The process involves extensive regulatory scrutiny and often generates significant media coverage. IPOs can lead to increased visibility and liquidity for the company, but they also come with risks for investors.",

    "What is short selling?": "Short selling is a trading strategy that involves borrowing shares of a stock to sell them at the current market price, with the intention of buying them back later at a lower price. While it can be profitable if the stock price declines, it also carries high risk, as potential losses are theoretically unlimited if the stock price rises.",

    "What is portfolio diversification?": "Portfolio diversification is a risk management strategy that involves spreading investments across different asset classes or sectors. This helps reduce exposure to any single investment's risk. A diversified portfolio may include stocks, bonds, real estate, and other assets, aiming to stabilize returns over time.",

    "What is a stock exchange?": "A stock exchange is a regulated marketplace where securities, including stocks and bonds, are bought and sold. It provides a platform for companies to raise capital by issuing shares and for investors to trade securities. Major exchanges like the NYSE and NASDAQ facilitate these transactions, ensuring transparency and fair pricing.",

    "What is fundamental analysis?": "Fundamental analysis is a method used to evaluate a security's intrinsic value by examining economic and financial factors. This includes analyzing a company's financial statements, management, market conditions, and overall economic indicators. Investors use this analysis to determine whether a stock is undervalued or overvalued relative to its true worth.",

    "What is technical analysis?": "Technical analysis involves using historical price data and trading volumes to forecast future price movements. Analysts utilize charts and various indicators to identify patterns, trends, and market behaviors. This approach is commonly favored by traders looking to capitalize on short-term price fluctuations rather than long-term investment.",

    "What are blue-chip stocks?": "Blue-chip stocks are shares in large, well-established companies with a history of reliable earnings and stable performance. These companies typically have strong fundamentals and are less volatile than smaller firms. Investing in blue-chip stocks is often seen as a safe strategy for conservative investors seeking consistent returns and dividends.",

    "What is a stockbroker?": "A stockbroker is a licensed professional who buys and sells stocks on behalf of clients. They provide advice on investment strategies and market trends, helping clients navigate the complexities of the stock market. Brokers earn commissions on trades and can work for brokerage firms or operate independently.",

    "What is a market order?": "A market order is an instruction to buy or sell a stock immediately at the current market price. Market orders are executed quickly, making them suitable for investors looking to enter or exit positions without delay. However, the final price may differ from the expected price, especially during volatile market conditions.",

    "What is a limit order?": "A limit order is an order to buy or sell a stock at a specified price or better. This gives investors more control over the price at which transactions occur. For example, a buy limit order will only execute at the limit price or lower, while a sell limit order will execute at the limit price or higher. Limit orders help manage trades without constant market monitoring.",

    "What is a stock index?": "A stock index is a measurement of the value of a section of the stock market, calculated from the prices of selected stocks. It serves as a benchmark for overall market performance. Well-known indices like the S&P 500 and the Dow Jones Industrial Average provide insights into market trends and economic health.",

    "What is volatility?": "Volatility refers to the degree of variation in a trading price series over time. High volatility indicates that a stock's price can change dramatically within a short period, presenting both opportunities and risks for investors. Understanding volatility is crucial for assessing potential investment risks and making informed decisions.",

    "What are stock options?": "Stock options are contracts granting the holder the right, but not the obligation, to buy or sell a stock at a predetermined price within a specific time frame. They can be used for hedging or speculation and are often part of employee compensation packages. Options can offer significant leverage, but they also come with risks.",

    "What is insider trading?": "Insider trading refers to buying or selling stocks based on non-public, material information about a company. While legal when done in compliance with regulations, illegal insider trading undermines market integrity and can result in severe penalties. Regulatory bodies like the SEC monitor trading activities to prevent such misconduct.",

    "What are mutual funds?": "Mutual funds pool money from multiple investors to purchase a diversified portfolio of stocks, bonds, or other securities. Managed by professional fund managers, these funds allow investors to benefit from diversification without needing to manage individual securities. They often come with management fees, which can impact overall returns.",

    "What is dollar-cost averaging?": "Dollar-cost averaging is an investment strategy that involves regularly investing a fixed amount of money into a particular stock or fund, regardless of its price. This approach reduces the impact of market volatility and helps investors avoid trying to time the market. It encourages disciplined investing and can lead to better long-term returns.",

    "What is a 401(k)?": "A 401(k) is a tax-advantaged retirement savings plan offered by employers, allowing employees to save for retirement while benefiting from tax breaks. Employees can contribute a portion of their salary, often with employer matching contributions. This type of plan helps individuals build a nest egg for retirement, promoting financial security.",

    "What is an index fund?": "An index fund is a type of mutual fund or ETF that aims to replicate the performance of a specific index, such as the S&P 500",

    "What is the Federal Reserve?": "The Federal Reserve, often referred to as the Fed, is the central banking system of the United States. It regulates the nation’s monetary policy by influencing money supply, interest rates, and inflation. The Fed plays a critical role in stabilizing the economy, ensuring banking system stability, and providing financial services to the government and financial institutions.",

    "What is inflation?": "Inflation is the rate at which the general level of prices for goods and services rises, eroding purchasing power. Central banks, such as the Federal Reserve, monitor inflation to implement policies that stabilize the economy. Moderate inflation is considered a sign of a growing economy, but high inflation can lead to uncertainty and reduced consumer spending.",

    "What is deflation?": "Deflation is the decrease in the general price level of goods and services, leading to increased purchasing power. While it may sound beneficial, deflation can indicate a declining economy, reduced consumer spending, and lower business revenues. Central banks often combat deflation by implementing monetary policies to encourage borrowing and spending.",
}

# Streamlit app layout
st.title("Stock Market Prediction 📈")
st.markdown("---")

# User Input
st.sidebar.header("Select Stock")
stocks = (
    "AAPL", "MSFT", "GOOG", "AMZN", "TSLA",
    "NFLX", "NVDA", "BRK-B", "JPM", "V", "JNJ",
    "PG", "UNH", "DIS", "HD", "MA", "VZ", "PYPL",
    "INTC",
)

selected_stock = st.sidebar.selectbox("Choose a stock:", stocks)
n_days = st.sidebar.text_input("Days of Prediction:", "30")

# Validate input
try:
    period = int(n_days)
    if period < 1 or period > 365:
        st.error("Enter a valid number of days (1-365).")
        period = 30
except ValueError:
    st.error("Please enter a valid number.")
    period = 30

@st.cache_data
def load_data(ticker):
    return yf.download(ticker, start="2020-01-01", end=datetime.today().strftime("%Y-%m-%d"))

data_load_state = st.text("Loading Data...")
data = load_data(selected_stock)
data_load_state.text("Data loaded successfully!")

# Recent Stock Data
st.markdown("<h2>Recent Stock Data</h2>", unsafe_allow_html=True)
st.dataframe(data, use_container_width=True)

# Moving Averages
data['MA_10'] = data['Close'].rolling(window=10).mean()
data['MA_30'] = data['Close'].rolling(window=30).mean()
data.reset_index(inplace=True)

full_date_range = pd.date_range(start=data['Date'].min(), end=data['Date'].max())
data = data.set_index('Date').reindex(full_date_range).ffill().reset_index()
data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'MA_10', 'MA_30']

series = TimeSeries.from_dataframe(data, 'Date', 'Close', fill_missing_dates=True)
model = ExponentialSmoothing()
model.fit(series)

forecast = model.predict(n=period)
future_index = pd.date_range(start=data['Date'].iloc[-1] + pd.Timedelta(days=1), periods=period)

forecast_df = pd.DataFrame({
    'Date': future_index,
    'Forecast': forecast.values().flatten()
})

# Display the historical close price
st.markdown("<h2>Future Prediction (Graph)</h2>", unsafe_allow_html=True)
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Historical Close", mode='lines', line=dict(color='#3498DB')))
fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecast'], name="Future Prediction", mode='lines', line=dict(color='green')))

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Stock Price',
    xaxis_rangeslider_visible=True,
    height=600,
    width=1000,
    hovermode="x"
)
st.plotly_chart(fig)

# Future prediction based on user input date using a date picker
st.markdown("<h2>Future Prediction</h2>", unsafe_allow_html=True)
input_date = st.date_input("Select a Future Date:", datetime.today().date())

if input_date:
    user_date = pd.to_datetime(input_date)

    if user_date <= datetime.today():
        st.error("Select a future date.")
    else:
        last_data_date = pd.to_datetime(data['Date'].iloc[-1])
        days_to_predict = (user_date - last_data_date).days

        if days_to_predict >= 0:
            future_forecast = model.predict(n=days_to_predict + 1)
            future_value = future_forecast.values().flatten()[-1]

            future_forecast_df = pd.DataFrame({
                'Date': [user_date],
                'Forecast': [future_value]
            })

            fig_future = go.Figure()
            fig_future.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Historical Close", mode='lines', line=dict(color='#3498DB')))
            fig_future.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecast'], name="Future Prediction", mode='lines', line=dict(color='green')))
            fig_future.add_trace(go.Scatter(
                x=future_forecast_df['Date'],
                y=future_forecast_df['Forecast'],
                mode='markers',
                marker=dict(color='red', size=12, symbol='circle'),
                name='Selected Future Date'
            ))

            fig_future.update_layout(
                title_text=f"Future Prediction for {user_date.date()}",
                xaxis_title='Date',
                yaxis_title='Stock Price',
                xaxis_rangeslider_visible=True,
                height=600,
                width=1000
            )
            st.plotly_chart(fig_future)

st.markdown("---")

# Fetch news articles for the selected stock
news_data = yf.Ticker(selected_stock).news

# Display news articles
st.markdown("<h2>Latest News</h2>", unsafe_allow_html=True)
st.write("Here are the most recent news articles related to the selected stock:")

for article in news_data[:3]:  # Display the top 3 news articles
    title = article['title']
    link = article['link']
    st.markdown(f"**{title}**")
    st.markdown(f"[Read more]({link})")

# Chatbot feature in the right sidebar
st.sidebar.header("💬 Chatbot")
st.sidebar.markdown("<div style='background-color: #f9f9f9; border-radius: 10px; padding: 10px;'>", unsafe_allow_html=True)
st.sidebar.markdown("**Select a question about stocks and investments!**")

# Dropdown for predefined questions
selected_question = st.sidebar.selectbox("Choose a question:", list(qa_pairs.keys()), index=0)

if st.sidebar.button("Submit"):
    if selected_question != st.session_state.get('last_question', ''):
        answer = qa_pairs[selected_question]

        # Save the last question and answer
        st.session_state.last_question = selected_question
        st.session_state.last_answer = answer

        # Display the answer
        st.sidebar.markdown(f"<div style='padding: 10px; background-color: #e6f7ff; border-radius: 5px; color: black;'><strong>Answer:</strong> {answer}</div>", unsafe_allow_html=True)

st.sidebar.markdown("</div>", unsafe_allow_html=True)


# Volume graph
st.markdown("<h2>Volume Traded</h2>", unsafe_allow_html=True)
fig_volume = go.Figure()
fig_volume.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name="Volume", marker_color='rgba(255, 153, 51, 0.6)'))

fig_volume.update_layout(
    xaxis_title='Date',
    yaxis_title='Volume',
    height=400,
    width=1000
)
st.plotly_chart(fig_volume)

# Weekly trends
st.markdown("<h2>Weekly Trends</h2>", unsafe_allow_html=True)
data['Week'] = data['Date'].dt.to_period('W').astype(str)
weekly_data = data.groupby('Week').agg({'Close': 'mean'}).reset_index()

fig_weekly = go.Figure()
fig_weekly.add_trace(go.Scatter(x=weekly_data['Week'], y=weekly_data['Close'], name="Weekly Trend", mode='lines', line=dict(color='blue')))

fig_weekly.update_layout(
    xaxis_title='Week',
    yaxis_title='Average Close Price',
    height=400,
    width=1000
)
st.plotly_chart(fig_weekly)

# Monthly trends
st.markdown("<h2>Monthly Trends</h2>", unsafe_allow_html=True)
data['Month'] = data['Date'].dt.to_period('M').astype(str)
monthly_data = data.groupby('Month').agg({'Close': 'mean'}).reset_index()

fig_monthly = go.Figure()
fig_monthly.add_trace(go.Scatter(x=monthly_data['Month'], y=monthly_data['Close'], name="Monthly Trend", mode='lines', line=dict(color='green')))

fig_monthly.update_layout(
    xaxis_title='Month',
    yaxis_title='Average Close Price',
    height=400,
    width=1000
)
st.plotly_chart(fig_monthly)

